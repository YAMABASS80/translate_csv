import argparse
import yaml
import csv
import boto3
import threading
import codecs
import os.path

parser = argparse.ArgumentParser(
    description='CSV translater using Amazon Translate.')
parser.add_argument(
    '-c','--csv-file',
    action='store',
    dest='csv_file',
    default='translate.csv',
    help='Source csv file for translate, default=translate.csv'
)
parser.add_argument(
    '-s','--source-lang-code','--from',
    action='store',
    dest='source_lang_code',
    choices=["ar","zh","zh-TW","cs","fr","de","en","it","ja","pt","ru","es","tr"],
    required=True,
    help='Source language code.'
)
parser.add_argument(
    '-t','--target-lang-code','--to',
    action='store',
    dest='target_lang_code',
    choices=["ar","zh","zh-TW","cs","fr","de","en","it","ja","pt","ru","es","tr"],
    required=True,
    help='Target language code.'
)
parser.add_argument(
    '--concurrency',
    action='store',
    dest='concurrency',
    type=int,
    default=36,
    help='Translation task concurrency. Default=36'
)
parser.add_argument(
    '--timeout',
    action='store',
    dest='timeout',
    type=int,
    default=10,
    help='Single translation task timeout. Default=10'
)

args = parser.parse_args()
csv_file = args.csv_file
source_lang_code = args.source_lang_code
target_lang_code = args.target_lang_code
concurrency = args.concurrency
timeout = args.timeout

translated_csv_file = os.path.splitext(csv_file)[0] + '_' + target_lang_code + os.path.splitext(csv_file)[1]

translate = boto3.client('translate', region_name='us-east-1')

class Translate(threading.Thread):
    def __init__(self, text_id, text, source_lang_code, target_lang_code):
        threading.Thread.__init__(self)
        self.text_id = text_id
        self.text = text
        self.source_lang_code = source_lang_code
        self.target_lang_code = target_lang_code
        self.result = None

    def get_result(self):
        return self.result

    def run(self):
        request = {
            'Text' : self.text,
            'SourceLanguageCode' : self.source_lang_code,
            'TargetLanguageCode' : self.target_lang_code
        }
        translated_text = translate.translate_text(**request)['TranslatedText']
        self.result = {
            "TextId" : self.text_id,
            "SourceText" : self.text,
            "TranslatedText" : translated_text.encode('shift_jis')
        }

# -- main ---
max_threads = 36
thread_timeout = 10
threads = []

with codecs.open(csv_file,'r',"utf-8", "ignore") as f:
    reader = csv.DictReader(f)

    # Start translation with parallel
    print('Translation tasks started.' )
    results = []
    for row in reader:
        thread = Translate(row['TextId'],row['SourceText'],source_lang_code,target_lang_code)
        thread.start()
        threads.append(thread)
        active_threads = threading.activeCount() - 1

        # When active threads reaches max threads, suspend threads and collect result.
        if active_threads > max_threads:
            for thread in threads:
                thread.join(thread_timeout)

    # Wait all threads completed
    for thread in threads:
        thread.join(thread_timeout)

    # Get translated result to write out.
    for thread in threads:
        results.append(thread.get_result())

    # Sort as source file
    sorted_results = sorted(results, key=lambda x: x['TextId'])

# Write out
with open(translated_csv_file, "w") as f:
    header = [
        "TextId",
        "SourceText",
        "TranslatedText"
    ]
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for row in sorted_results:
        writer.writerow(row)

print('Translation tasks finished. result files: ' + translated_csv_file  )
