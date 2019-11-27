# SCProject
Repo for social computing project.
## How to Run...
### Making requests to the reddit api
The below will get all comments from the pittsburgh reddit between October 27th 2018 and November 27th 2018 (EST):
```console
foo@bar:~$ python3 request.py pittsburgh 2018-10-27-00:00:00 2018-11-27-00:00:00
```
### Classifying comments
Running the script classifer.py writes out the file about_shooting.txt which lists all of the reddit posts about the shooting. This is based on whether the post or any comment within the post contains the word with the stem "shoot" or "shooter".
E.g. this would include "shooting", "shootings", "shooters", etc. Note that a post contains multiple comments.

### Making word-vectors
Running the script comment2vector.py makes vectors for all comments in within the posts in about_shooting.txt. The vectors are written to vecs.txt with indexing by the sentence_index.txt provided.

## Task Recap
Tasks 11-17:

1. Pick cities
2. Rule based Classifier
3. Split by time: 
   Be able to get the week, day, month and year of the shooting. Time stamp in Eastern Time to make it easier.
4. Topic modeling
