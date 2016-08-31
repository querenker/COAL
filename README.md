# COAL
[![Build Status](https://travis-ci.org/querenker/COAL.svg?branch=master)](https://travis-ci.org/querenker/COAL)

### ☃ Unicode snowman is here to make you happy! ☃

web media content analysis framework

word list (words.txt) taken from https://github.com/dwyl/english-words, which is based on the word list from  http://www.infochimps.com/datasets/word-list-350000-simple-english-words-excel-readable.

This is a SuperAmazingProject

## Coming Soon...
![Fluffy](http://pa1.narvii.com/5914/bd6025761c9c5b17ebf6fb06d63da1c823bd3871_hq.gif)

## How to Use

### Requirements, Compilation

- JDK, maven
- Python 3

```
cd /path/to/coal/repository
mvn compile
```

```
cd /path/to/coal/repository
pip install -r python-worker/requirements.txt
```

### Launching COAL + worker

#### Main Server

```
cd /path/to/coal/repository
mvn exec java@main
```

#### Download Worker

```
cd /path/to/coal/repository
mvn exec java@downloadworker
```

#### Update Worker

```
cd /path/to/coal/repository
mvn exec java@updateworker
```

#### Author Extraction Worker

```
cd /path/to/coal/repository
./python-worker/pdf_author_extraction_worker.py
```

#### Image Extraction Worker

```
cd /path/to/coal/repository
./python-worker/pdf_image_extraction_worker.py
```

#### Image Recognition Worker

```
cd /path/to/coal/repository
CLARIFAI_APP_ID=<APP-ID> CLARIFAI_APP_SECRET=<APP-SECRET> ./python-worker/clarifai_worker.py
```

#### PDF Metadata Extraction Worker

```
cd /path/to/coal/repository
./python-worker/pdf_metadata_extraction_worker.py
```

#### Text Extraction Worker

```
cd /path/to/coal/repository
./python-worker/pdf_text_extraction_worker.py
```

#### Text Formatting Worker

```
cd /path/to/coal/repository
./python-worker/pdf_text_formatting_worker.py
```

#### Keyword Extraction Worker

```
cd /path/to/coal/repository
./python-worker/pdf_text_keyword_extraction_worker.py
```

#### Language Detection Worker

```
cd /path/to/coal/repository
./python-worker/pdf_text_langdetect_worker.py
```

#### Named Entity Linking Worker

```
cd /path/to/coal/repository
./python-worker/pdf_text_named_entity_linking_worker.py
```