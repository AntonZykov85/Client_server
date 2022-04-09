import subprocess
import chardet

FIRST_ARGS = ['ping', 'yandex.ru']
SECOND_ARGS = ['ping', 'youtube.com']
yandex_ping = subprocess.Popen(FIRST_ARGS, stdout=subprocess.PIPE)
youtube_ping = subprocess.Popen(SECOND_ARGS, stdout=subprocess.PIPE)

# for line in yandex_ping.stdout:
#     result = chardet.detect(line)
#     print(result)
#     line = line.decode(result['encoding']).encode('utf-8')
#     print(line.decode('utf-8'))

for line in youtube_ping.stdout:
    result = chardet.detect(line)
    print(result)
    line = line.decode(result['encoding']).encode('utf-8')
    print(line.decode('utf-8'))