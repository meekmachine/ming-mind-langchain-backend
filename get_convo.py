import argparse
import pandas as pd
from convokit import Corpus, download

# Set up command line arguments
""" COmmented out for now
parser = argparse.ArgumentParser(description='Process conversation dataset.')
parser.add_argument('--min_messages', type=int, default=0, help='Minimum number of messages in a conversation')
parser.add_argument('--has_personal_attack', type=bool, default=False, help='Whether the conversation includes a personal attack')
parser.add_argument('--download',type=bool,default=False)
args = parser.parse_args()
print(args)
"""
min_messages = 0
has_personal_attack = False
year = 2018
load = False # True -> need to download the dataset False -> if not

DATA_DIR = 'data-convs-awry' #put the current dir here
if load: #args.download:
    AWRY_ROOT_DIR = download('conversations-gone-awry-corpus',data_dir=DATA_DIR)
    print(AWRY_ROOT_DIR)
else: 
    AWRY_ROOT_DIR = 'data-convs-awry\\conversations-gone-awry-corpus' # if you are

awry_corpus = Corpus(AWRY_ROOT_DIR)

def filter_conversations(corpus, min_messages = 0, has_personal_attack = None,year = None):
  convos = []
  for convo in corpus.iter_conversations():
      # then use iter_utterances at the Conversation level to count the number of comments in each post
      # (the Conversation-level iter_utterances iterates over Utterances in that Conversation only)
      n_comments = len([u for u in convo.iter_utterances()])
      if has_personal_attack != None:
        convo_has_attack_filter = convo.meta['conversation_has_personal_attack'] == has_personal_attack
      else:
        convo_has_attack_filter = True

      if year != None:
        year_filter = convo.meta['year'] == year
      else:
        year_filter = True
      if (n_comments >= min_messages) and (convo_has_attack_filter) and (year_filter):
          convos.append(convo)
  return convos

# you can add more attributes such as total amount of personal attacks and toxicity
def convo_to_df(convo):
  df = convo.get_utterances_dataframe()
  df['conversation_id'] = convo.id
  #you can create more attributes here
  return df

def convos_to_dfs(convos):
  dfs = []
  for convo in convos:
    dfs.append(convo_to_df(convo))
  return pd.concat(dfs) # do you want to concatinate the dfs or have the seperate dfs be 

# We can edit this file as we go to use it as a file used to import into other files


#filter_conversations(awry_corpus,min_messages=50,has_personal_attack=True)