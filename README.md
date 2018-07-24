# translate_csv

## What is this?
CSV based batch translation tool. This tool utilize Amazon Translate api, so before you use this you need AWS account and credential.
- Amazon Translate
https://aws.amazon.com/translate/?nc1=h_ls




## Prerequests
1. Setup your AWS credential
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

2. Install boto3(aws sdk for python)
https://aws.amazon.com/sdk-for-python/?nc1=h_ls

## How to use
- Source file preparation
CSV file format is super simple. The requirement for csv file is only consecutive _TextId_ and _SourceText_ header.

```
TextId,SourceText
1,Hello
```

- Basic command line

```
translate_csv.py -s <Source langage code> -t <Target language code> -c <source csv file.>
```

And you will get ouput file as "source csv file" + _LanguageCode_ + .csv. For example you tranlated English from Japanese then the output file name will be translate_ja.csv


- Advanced Option
If you have performance trouble, try increase concurrency using '--concurrency' option.