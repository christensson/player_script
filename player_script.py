#!/usr/bin/python3

import argparse
import logging
import urllib.request
import json
import pprint
import subprocess

def createParser():
    parser = argparse.ArgumentParser(description='Player script, wrapper to pirateplayer')
    parser.add_argument(
        '-v,', '--verbose', dest='verbosity',
        action='count', default=0,
        help='Enable verbosity')
    parser.add_argument(
        '-p', '--player', dest='player_cmd',
        action='store', type=str, default='omxplayer',
        help='Video player command [default=%(default)s]')
    parser.add_argument(
        '-u', '--url', dest='source_url',
        action='store', type=str, required=True,
        help='Source URL of video')
    parser.add_argument(
        '-l', '--list_only', dest='list_streams_only',
        action='store_true',
        help='Do not play, only list streams.')
    parser.add_argument(
        '--pirate_play_api_url', dest='pirate_play_api_url',
        action='store', type=str,
        default='http://pirateplay.se/api/get_streams.js',
        help='Pirate player api URL (json). [default=%(default)s]') 
    parser.add_argument(
        '-i', '--id', dest='stream_id',
        action='store', type=int, default=0,
        help='Play stream with id. Use --no_play [default=%(default)s]') 
    return parser

def init_log(verbosity):
    log = logging.getLogger('root')
    if verbosity > 1:
        log.setLevel(logging.DEBUG)
        pass
    elif verbosity > 0:
        log.setLevel(logging.INFO)
        pass
    else:
        log.setLevel(logging.WARNING)
        pass
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s(): - %(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(consoleHandler)
    return log

class VideoStreams:
    def __init__(self, args, log):
        self.args = args
        self.log = log
        pass
    
    def get_video_streams(self, source_url):
        url = self.args.pirate_play_api_url + '?url=' + source_url
        self.log.debug('Request URL: %s' % (url))
        json_str_data = urllib.request.urlopen(url).read().decode()
        self.video_streams_data = json.loads(json_str_data)
        self.log.debug('Data:\n%s' % (pprint.pformat(self.video_streams_data)))
        pass

    def format_streams(self, show_urls=False):
        str = 'Found video streams:\n'
        count = 0
        for s in self.video_streams_data:
            str = str + ('  Stream %d with quality %s\n' %
                         (count, s['meta']['quality']))
            if show_urls:
                str = str + ('    URL: %s\n' % (s['url']))
            count = count + 1
            pass
        return str

    def get_stream_url(self, stream_id):
        return self.video_streams_data[stream_id]['url']

def main():
    parser = createParser()
    args = parser.parse_args()

    log = init_log(args.verbosity)
    log.info('Pirateplayer wrapper script started!')
    log.debug('Args: %s', str(args))

    video_streams = VideoStreams(args, log)
    video_streams.get_video_streams(args.source_url)
    print(video_streams.format_streams(show_urls=args.list_streams_only))
    stream_url = video_streams.get_stream_url(args.stream_id)
    print('Requested stream %d with URL %s' %
          (args.stream_id, stream_url))
    if not args.list_streams_only:
        print('Starting player %s' % (args.player_cmd))
        cmd = [args.player_cmd, stream_url]
        log.debug('Player cmd=%s' % (str(cmd)))
        subprocess.call(cmd, shell=False)
        pass
    pass

if __name__ == "__main__":
    main()
