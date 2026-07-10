#include "livox_lidar_api.h"
#include "livox_lidar_def.h"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>

namespace {

std::string g_current_ip;
LivoxLidarIpInfo g_new_ip{};
std::atomic<bool> g_command_sent{false};
std::mutex g_mutex;
std::condition_variable g_cv;
bool g_done = false;
bool g_success = false;

void Finish(bool success) {
  {
    std::lock_guard<std::mutex> lock(g_mutex);
    g_done = true;
    g_success = success;
  }
  g_cv.notify_one();
}

void RebootCallback(livox_status status, uint32_t handle,
                    LivoxLidarRebootResponse* response, void*) {
  if (status == kLivoxLidarStatusSuccess && response != nullptr && response->ret_code == 0) {
    std::printf("Reboot request accepted (handle=%u).\n", handle);
  } else {
    std::printf("Warning: reboot request was not acknowledged; power-cycle the LiDAR manually.\n");
  }
}

void SetIpCallback(livox_status status, uint32_t handle,
                   LivoxLidarAsyncControlResponse* response, void*) {
  if (status != kLivoxLidarStatusSuccess || response == nullptr) {
    std::fprintf(stderr, "SetLivoxLidarIp failed or timed out (status=%d).\n", status);
    Finish(false);
    return;
  }

  std::printf("Set-IP response: ret_code=%u, error_key=%u\n",
              response->ret_code, response->error_key);
  if (response->ret_code != 0 || response->error_key != 0) {
    Finish(false);
    return;
  }

  std::printf("IP configuration accepted: %s / %s, gateway %s\n",
              g_new_ip.ip_addr, g_new_ip.net_mask, g_new_ip.gw_addr);
  LivoxLidarRequestReboot(handle, RebootCallback, nullptr);
  Finish(true);
}

void LidarInfoChangeCallback(uint32_t handle, const LivoxLidarInfo* info, void*) {
  if (info == nullptr) {
    return;
  }

  std::printf("Discovered LiDAR: type=%u, SN=%s, IP=%s\n",
              info->dev_type, info->sn, info->lidar_ip);

  if (info->dev_type != kLivoxLidarTypeMid360s || g_current_ip != info->lidar_ip) {
    return;
  }

  bool expected = false;
  if (!g_command_sent.compare_exchange_strong(expected, true)) {
    return;
  }

  std::printf("Matched MID360s at %s; sending SetLivoxLidarIp...\n", info->lidar_ip);
  const livox_status status = SetLivoxLidarIp(handle, &g_new_ip, SetIpCallback, nullptr);
  if (status != kLivoxLidarStatusSuccess) {
    std::fprintf(stderr, "SetLivoxLidarIp could not be queued (status=%d).\n", status);
    Finish(false);
  }
}

bool CopyArg(char (&dest)[16], const char* src, const char* name) {
  if (std::strlen(src) >= sizeof(dest)) {
    std::fprintf(stderr, "%s is too long: %s\n", name, src);
    return false;
  }
  std::strcpy(dest, src);
  return true;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 6) {
    std::fprintf(stderr,
        "Usage: %s <config.json> <current-ip> <new-ip> <netmask> <gateway>\n"
        "Example: %s mid360s_config.json 192.168.1.139 192.168.123.20 "
        "255.255.255.0 192.168.123.1\n",
        argv[0], argv[0]);
    return 2;
  }

  g_current_ip = argv[2];
  if (!CopyArg(g_new_ip.ip_addr, argv[3], "new IP") ||
      !CopyArg(g_new_ip.net_mask, argv[4], "netmask") ||
      !CopyArg(g_new_ip.gw_addr, argv[5], "gateway")) {
    return 2;
  }

  std::printf("Target: MID360s currently at %s\n", g_current_ip.c_str());
  std::printf("New network: %s / %s, gateway %s\n",
              g_new_ip.ip_addr, g_new_ip.net_mask, g_new_ip.gw_addr);

  if (!LivoxLidarSdkInit(argv[1])) {
    std::fprintf(stderr, "LivoxLidarSdkInit failed. Check the host IP in the JSON file.\n");
    return 1;
  }
  SetLivoxLidarInfoChangeCallback(LidarInfoChangeCallback, nullptr);

  std::unique_lock<std::mutex> lock(g_mutex);
  const bool completed = g_cv.wait_for(lock, std::chrono::seconds(30), [] { return g_done; });
  const bool success = completed && g_success;
  lock.unlock();

  if (!completed) {
    std::fprintf(stderr, "Timed out: MID360s at %s was not discovered within 30 seconds.\n",
                 g_current_ip.c_str());
  }
  if (success) {
    std::this_thread::sleep_for(std::chrono::seconds(2));
  }
  LivoxLidarSdkUninit();
  return success ? 0 : 1;
}
