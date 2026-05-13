#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAV 转 MP3 转换工具
用法: python convert_wav_to_mp3.py <input.wav> [output.mp3]
"""

import sys
import os
import subprocess
import argparse


def get_audio_info(file_path):
    """获取音频文件信息"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration,size,bit_rate',
            '-show_entries', 'stream=sample_rate,channels,codec_name',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            stream = data.get('streams', [{}])[0]
            format_info = data.get('format', {})
            
            return {
                'sample_rate': stream.get('sample_rate', 'N/A'),
                'channels': stream.get('channels', 'N/A'),
                'codec': stream.get('codec_name', 'N/A'),
                'duration': format_info.get('duration', 'N/A'),
                'size': format_info.get('size', 'N/A'),
                'bit_rate': format_info.get('bit_rate', 'N/A')
            }
    except Exception as e:
        print(f"⚠️ 无法获取文件信息: {e}")
        return None


def convert_wav_to_mp3(input_file, output_file=None, sample_rate=16000, channels=1, bitrate='128k'):
    """
    将 WAV 文件转换为 MP3
    
    :param input_file: 输入 WAV 文件路径
    :param output_file: 输出 MP3 文件路径（可选，默认替换扩展名）
    :param sample_rate: 输出采样率（默认 16000 Hz）
    :param channels: 输出声道数（默认 1，单声道）
    :param bitrate: 输出比特率（默认 128k）
    """
    
    # 检查输入文件
    if not os.path.exists(input_file):
        print(f"❌ 错误: 文件不存在: {input_file}")
        return False
    
    # 确定输出文件名
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    print("\n" + "="*60)
    print("🎵 WAV 转 MP3 转换工具")
    print("="*60)
    print(f"  输入文件: {input_file}")
    print(f"  输出文件: {output_file}")
    print(f"  采样率: {sample_rate} Hz")
    print(f"  声道数: {channels}")
    print(f"  比特率: {bitrate}")
    print("="*60)
    
    # 获取输入文件信息
    print("\n📊 输入文件信息:")
    input_info = get_audio_info(input_file)
    if input_info:
        print(f"  采样率: {input_info['sample_rate']} Hz")
        print(f"  声道数: {input_info['channels']}")
        print(f"  编码: {input_info['codec']}")
        print(f"  时长: {input_info['duration']} 秒")
        print(f"  大小: {int(input_info['size']) / 1024:.2f} KB")
    
    # 构建 ffmpeg 命令
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-ar', str(sample_rate),
        '-ac', str(channels),
        '-b:a', bitrate,
        '-acodec', 'libmp3lame',
        '-loglevel', 'error',
        output_file
    ]
    
    # 执行转换
    print("\n🔄 开始转换...")
    try:
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 转换成功!")
            
            # 获取输出文件信息
            print("\n📊 输出文件信息:")
            output_info = get_audio_info(output_file)
            if output_info:
                print(f"  采样率: {output_info['sample_rate']} Hz")
                print(f"  声道数: {output_info['channels']}")
                print(f"  编码: {output_info['codec']}")
                print(f"  时长: {output_info['duration']} 秒")
                print(f"  大小: {int(output_info['size']) / 1024:.2f} KB")
            
            # 文件大小对比
            if input_info and output_info:
                input_size = int(input_info['size'])
                output_size = int(output_info['size'])
                compression_ratio = (1 - output_size / input_size) * 100
                
                print(f"\n📦 文件大小对比:")
                print(f"  输入: {input_size / 1024:.2f} KB")
                print(f"  输出: {output_size / 1024:.2f} KB")
                print(f"  压缩率: {compression_ratio:.1f}%")
            
            # 播放提示
            print(f"\n💡 播放命令:")
            print(f"  ffplay \"{output_file}\"")
            
            return True
        else:
            print(f"❌ 转换失败!")
            if result.stderr:
                print(f"错误信息: {result.stderr.decode()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 转换超时!")
        return False
    except Exception as e:
        print(f"❌ 转换异常: {e}")
        return False


def batch_convert(directory, pattern='*.wav'):
    """批量转换目录中的 WAV 文件"""
    import glob
    
    wav_files = glob.glob(os.path.join(directory, pattern))
    
    if not wav_files:
        print(f"❌ 在 {directory} 中未找到 {pattern} 文件")
        return
    
    print(f"\n找到 {len(wav_files)} 个 WAV 文件:")
    for f in wav_files:
        print(f"  - {os.path.basename(f)}")
    
    print("\n开始批量转换...\n")
    
    success_count = 0
    for wav_file in wav_files:
        if convert_wav_to_mp3(wav_file):
            success_count += 1
        print()
    
    print("="*60)
    print(f"✅ 批量转换完成: {success_count}/{len(wav_files)} 成功")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='WAV 转 MP3 转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  %(prog)s input.wav
  
  # 指定输出文件名
  %(prog)s input.wav output.mp3
  
  # 自定义参数
  %(prog)s input.wav -r 48000 -c 2 -b 320k
  
  # 批量转换
  %(prog)s --batch /tmp/debug_*.wav
        """
    )
    
    parser.add_argument('input', nargs='?', help='输入 WAV 文件')
    parser.add_argument('output', nargs='?', help='输出 MP3 文件（可选）')
    parser.add_argument('-r', '--sample-rate', type=int, default=16000, 
                        help='采样率 (默认: 16000)')
    parser.add_argument('-c', '--channels', type=int, default=1, 
                        help='声道数 (默认: 1)')
    parser.add_argument('-b', '--bitrate', default='128k', 
                        help='比特率 (默认: 128k)')
    parser.add_argument('--batch', metavar='PATTERN', 
                        help='批量转换（例如: /tmp/debug_*.wav）')
    
    args = parser.parse_args()
    
    # 批量转换模式
    if args.batch:
        import glob
        files = glob.glob(args.batch)
        if files:
            directory = os.path.dirname(files[0])
            pattern = os.path.basename(args.batch)
            batch_convert(directory or '.', pattern)
        else:
            print(f"❌ 未找到匹配的文件: {args.batch}")
        return
    
    # 单文件转换模式
    if not args.input:
        parser.print_help()
        return
    
    convert_wav_to_mp3(
        args.input,
        args.output,
        args.sample_rate,
        args.channels,
        args.bitrate
    )


if __name__ == '__main__':
    main()