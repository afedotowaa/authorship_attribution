## _Authorship attribution of Russian-language texts_



Comparison of deep neural network architectures and classical machine learning methods for authorship attribution of russian social media and literary texts includes:

- datasets demo versions
- texts preprocessing stage
- classical ML methods (KNN, SVM, LR, DT, RF, NB)
- deep models (LSTM, CNN, their hybrids, BERT)
- fastText


## DATASETS

- demo version of the social media dataset available at data folder 
- social media texts were anonymized for research (structure of the dataset - author id, comment_id, comment)
- Russian classic's texts were obtained from online-library http://www.lib.ru/
- literary demo consist of 300 authors and available online via https://disk.yandex.ru/d/0Z1b1nB0fuAz_Q
- to get full datasets please contact us 

Full social media dataset consists of:

| Number of author | 3075 |
| ------ | ------ |
| Number of texts  | 202 892 |
| Dataset size, symbols | 30 652 109 |
| Dataset size, words | 4 708 619 |
| The average length of text, symbols | 151.1 |
| The average length of text, words | 23.7 |
| The average number of texts per author | 115.37 |
## EXPERIMENTS

> note that all experiments were provided on Google colab using GPU ! 
> just download .ipynb files and open via colab, use ready-made dataset from .data or your own with similar structure. upload file with texts into colab and use noteboks! 


 
## TEXT PREPOCESSING

for texts preprocessing please use text_preprocessing .ipynb file and:

- transform text to lower case 
- whitespaces formatting
- removal of stop-words
- removal of digits (numbers) and special characters

## FEATURE SELECTION

use feature_selection .ipynb into collab and create your own feature space combining different features.
Let's take a look at 16 different functions, each of which is designed for text analysis.
There are several directions of text analysis, in this section we will pay special attention to frequency analysis, its implementation will help to form digital portraits of the studied authors. What's the point?
Based on the distribution of frequencies of parts of speech, letters of the Russian alphabet, certain words, it is possible to form the so-called unique writing style of each author, as well as to get an idea of ​​the direction, subject matter of the text

It is important to note that such frequency allocations are particularly effective when used together, i.e. the frequency distribution of exclusively parts of speech will not bring such a high result as a vector of many different characteristics of the writing style (hereinafter we will call them features). Why is this happening?

Suppose we have texts by two authors, both of whom are writing short stories for children. It is logical that the structure of sentences will not be complicated by many turns and complex (composed) / subordinate parts, since it is written for children. That is, according to the distribution of only parts of speech, it is very problematic to separate these two authors.
In addition, the texts cannot always be artistic and it is not so easy to establish on one or two grounds what is in common between messages on social networks and a business letter written by the same person.

try to use this functions on a simple way like this:

```sh
normalized_words = get_normalized_words(text)
```
on get_common_ngrams_words_freq and get_common_ngrams_letters_freq you can follow your own n parameter for a best result!

```sh
def get_common_ngrams_letters_freq(text, n, count=250):
    ngrams_list = ngrams_letters(text, n)
    counter = Counter(ngrams_list)
    common = counter.most_common(count)
    freq = {a[0]: a[1]/len(ngrams_list) for a in common}
    return freq
```

## CLASSICAL MACHINE LEARNING METHODS

we provide several efficient ML methods for authorship attribution. Use notebok and follow the comments on it. This part based on the Scikit-learn. It is one of the most widely used Python packages for Data Science and Machine Learning.
The main advantage is the many algorithms and excellent documentation about their classes, methods and functions. see link https://scikit-learn.org/stable/#

use feature space file formed on the previous stage or prepocessed texts. All results supported by visualization 

## DEEP MODELS

Want to use deep models? Great!

you need only colab with GPU and prepocessed texts.
select BERT notebook or other models (LSTM, CNN, their hybrids) and follow instructions in the notebok
Make a change in classifier parameters and get your best result!


## FASTTEXT

provide experiments with fastText using fastText.ipynb and dataset. Select n-grams and other parameters or default version

## FEATURE SEELCTION

GA.ipynb notebook will help you to get the best performance of ML methods. 
This notebook based on SVM, but you can use another classifier just replace clf to your method.


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
