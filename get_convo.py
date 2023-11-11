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


class ConvoGetter:
  def __init__(self,AWRY_ROOT_DIR = None) -> None:
    DATA_DIR = 'data-convs-awry' #put the current dir here
    if AWRY_ROOT_DIR == None: #args.download:
      self.AWRY_ROOT_DIR = download('conversations-gone-awry-corpus',data_dir=DATA_DIR)
    else:
      self.AWRY_ROOT_DIR = AWRY_ROOT_DIR  
    self.awry_corpus = Corpus(self.AWRY_ROOT_DIR)

  def filter_conversations(self, min_messages = 0, has_personal_attack = None,year = None):
    convos = []
    for convo in self.awry_corpus.iter_conversations():
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

        
        if (n_comments >= min_messages) and (convo_has_attack_filter) and (year_filter): #filter out convos with this if statement
            convos.append(convo)
    return convos

# you can add more attributes such as total amount of personal attacks and toxicity
# although personal attacks and toxicity per message appears
  def convo_to_df(self,convo):
    df = convo.get_utterances_dataframe()
    df['conversation_id'] = convo.id
    #you can create more attributes here
    return df

  def convos_to_dfs(self,convos,do_concat = False):
    dfs = []
    for convo in convos:
      dfs.append(self.convo_to_df(convo))
    if do_concat:
      dfs = pd.concat(dfs)
    return dfs
  

  # conversation to text - name, message (one string)
  # conversation to array of messages
  