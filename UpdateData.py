# Oona Leppänen

import numpy as np
import pandas as pd
import os
import glob

#################################################

# Credits from this code section to:
# https://stackoverflow.com/questions/29769181/count-the-number-of-folders-in-a-directory-and-subdirectories
# Counts the total number of files and folders in the directory. One file contains one drafted deck. One folder contains
# dekcs of one draft.
# Point is to count how many files there are. Not really other meaning and its rather pointless than nothing else.
# I could have done the same below and much more easier. But the point is to learn and that's why I decided to keep it.

total_files = 0
total_folders = 0

for _, dirnames, filenames in os.walk('Drafts'):
  # ^ this idiom means "we won't be using this value"
    total_files += len(filenames)
    total_folders += len(dirnames)

print('files (decks): {}, folders (drafts): {}'.format(total_files, total_folders))

#################################################

# Creates a list and then saves all decks to it: reads deck files and saves them to the list.
# Deletes unnecessary data from saved decks (removes the last 2 rows (date and how well the deck succeeded)) 
# and creates a new column for taging 0 or 1 depending on does a card belong to the deck or it's sideboard. 0 = belongs to deck,
# 1 = belongs to sideboard. Deletes useless row. Last takes a name of a deck and creates a csv file using the name as the csv files name.

s = []
# Write the path/file you want to open inside the parenthesis. The files used to create the starting data are from 'Drafts/*/*'.
open_file = glob.glob('New_drafts/*/*')
sideboard_tracked = 1

for x in range(0, len(open_file)):
    s.append(pd.read_csv(open_file[x], delimiter = '\n', engine = 'python', names = ['Number_of_card', 'Card_name']))#sep = 'x |\n|;'

    # There might be separator in multiple times, not just ones, so let's ignore all other places where there are separator mark
    # and do the split. [0] ignores other separator places and saves the name of the file in file_name. 
    # Saves the name of the deck to file_name for later use.
    file_name = os.path.basename(open_file[x])
    file_name = os.path.splitext(file_name)[0]
    print(file_name)
    
    # (Expand = expands splitted strings into separate columns.)
    #s[x]['Card_name'] = s[x].Number_of_card.str.split('x ', expand = True)[1]
    s[x][['Number_of_card', 'Card_name']] = s[x].Number_of_card.str.split('x ', n = 1, expand = True)#[0]
    
    # iloc[rows, columns]
    s[x] = s[x].iloc[:len(s[x])-4, :]
    s[x] = s[x].reset_index(drop=True)
    
    s[x]['Is_in_sideboard'] = 0
    sideboard_counter = 0
    row_added = 0
    length = len(s[x])
    i = 0
    
    while i < length:
        test_card = s[x].iloc[i]['Card_name']
        test_amount = s[x].iloc[i]['Number_of_card']
        
        if s[x].iloc[i][0] == 'Sideboard':
            sideboard_counter = 1
            sideboard_tracked = i
            
        elif sideboard_counter == 1:
            s[x].loc[i, 'Is_in_sideboard'] = 1
            
            if test_amount == '2':
                if (test_card != 'Plains') & (test_card != 'Island') & (test_card != 'Swamp') & (test_card != 'Mountain') & (test_card !='Forest'):
                    new_row = pd.DataFrame({'Number_of_card': [1], 'Card_name': [test_card], 'Is_in_sideboard': [1]})
                    s[x] = pd.concat([s[x], new_row], ignore_index = True, axis = 0)
                    s[x].loc[i, 'Number_of_card'] = 1
                    print(new_row)
        else:
            if test_amount == '2':
                if (test_card != 'Plains') & (test_card != 'Island') & (test_card != 'Swamp') & (test_card != 'Mountain') & (test_card !='Forest'):
                    new_row = pd.DataFrame({'Number_of_card': [1], 'Card_name': [test_card], 'Is_in_sideboard': [0]})
                    s[x] = pd.concat([new_row, s[x]], axis = 0).reset_index(drop = True)
                    
                    sideboard_tracked += 1
                    i += 1
                    s[x].loc[i, 'Number_of_card'] = 1
                    row_added = 1
                    length += 1
                    print(new_row)
                    # broodmoth tulee 2 kertaa deckiin jossa on 2 arid mesaa (listassa alhaalla)
        i += 1
        
    
    #  Deletes useless row.
    s[x] = s[x].drop(labels = [sideboard_tracked], axis = 0)
    s[x] = s[x].reset_index(drop=True)
    sideboard_tracked = 0
    print(s[x], '\n')
    # Write between the first apostrophes ('') the path/the name of the folder where you want to save the csv files.
    # The files used to create the starting data are saved in 'Drafts_csv/'.
    s[x].to_csv('New_drafts_csv/' + file_name + '.csv', sep = ';', index = False)

# print(s)
print('Number of decks in s: ', x+1)



##################




# Creating dataframe.

# The for loop creates a list which contains names and scores of the decks and the date the decks were drafted.
# The last line makes a dataframe out of 3 lists.

open_file = glob.glob('New_drafts/*/*')
decks = pd.read_csv('original_deck_data.csv', delimiter = ';') # must be changed to 'deck_data.csv'!!!!

for x in range(0, len(open_file)):
    file_name = os.path.basename(open_file[x])
    file_name = os.path.splitext(file_name)[0]
    
    df = pd.read_csv(open_file[x], delimiter = '\n', header = None)
    deck_date = df.iat[len(df)-4, 0]
    deck_result = df.iat[len(df)-3, 0]
    
    decks.loc[len(decks['Name']), 'Name'] = file_name
    decks.loc[len(decks['Date'])-1, 'Date'] = deck_date
    decks.loc[len(decks['Draft_result'])-1, 'Draft_result'] = deck_result
    decks.loc[len(decks['Same_date_different_draft'])-1, 'Same_date_different_draft'] = 'Draft 1'
    decks.loc[len(decks['In_card_data'])-1, 'In_card_data'] = 0

print(decks)
print(decks.iloc[110:130,:])

# There's new rows so their columns handling scores are filled here.
# Checks if there's been multiple drafts in the same date and adds the information about the second draft to
# Same_date_different_draft column if true.
# Scores are counted as follows: 3 points for 1 victory, 1.5 point for 1 draw and 0 point for loss.


for i in range(len(decks)-len(open_file), len(decks)):
    score = 0
    string = decks.iloc[i]['Draft_result']
    victory = string[0]
    loss = string[2]
    score_counter = 0
    
    if len(string) > 3:
        print(string)
        draw = string[4]
    else: draw = '0'
        
    # If ther's been draft 2 it the information is saved here.
    if len(string) > 12:
        # If the deck has draws.
        decks.loc[i, 'Same_date_different_draft'] = string[7:]
        print(string)
        
    elif len(string) > 5:
        # If the deck doesn't have draws.
        decks.loc[i, 'Same_date_different_draft'] = string[5:]
        print(string)
        
    if victory == '2':
        decks.loc[i, 'Victory'] = 2
        score_counter += 6
        
    elif victory == '1':
        decks.loc[i, 'Victory'] = 1
        score_counter += 3
        
    elif victory == '3':
        decks.loc[i, 'Victory'] = 3
        score_counter += 9
        
    elif victory == '0':
        decks.loc[i, 'Victory'] = 0
        
    else:
        decks.loc[i, 'Victory'] = 11111
    
    if loss == '2':
        decks.loc[i, 'Loss'] = 2
        
    elif loss == '1':
        decks.loc[i, 'Loss'] = 1
        
    elif loss == '3':
        decks.loc[i, 'Loss'] = 3
        
    elif loss == '0':
        decks.loc[i, 'Loss'] = 0
        
    else:
        decks.loc[i, 'Loss'] = 11111
    
    if draw == '2':
        decks.loc[i, 'Draw'] = 2
        score_counter += 3
        
    elif draw == '1':
        decks.loc[i, 'Draw'] = 1
        score_counter += 1.5
        
    elif draw == '3':
        decks.loc[i, 'Draw'] = 3
        score_counter += 4.5
        
    elif draw == '0':
        decks.loc[i, 'Draw'] = 0
    else:
        decks.loc[i, 'Draw'] = 11111

    decks.loc[i, 'Score'] = format(score_counter, '.5f')

# If there has been draft 2 it has been written after the result. The 'Draft 2' text must be removed and these 3 rows do just that.
draft_result_list = decks.Draft_result
draft_result_list = draft_result_list.iloc[110:130]
decks.loc[110:130, ['Draft_result']] = draft_result_list.str.split(',', expand = True)[0] # Saves only the results to Draft_result column.

print(decks.loc[110:130, ['Score']])
print(decks.loc[:, ['Draft_result']].values)

# There's new rows so their columns handling colors and types are filled here.

s = []
colors = []
types = []

for x in range(0, len(open_file)):
    file_name = os.path.basename(open_file[x])
    file_name = os.path.splitext(file_name)[0]
    
    s.append(pd.read_csv(open_file[x], delimiter = '\n', engine = 'python', names = ['Color_type']))
    
    for i in range(len(decks)-len(open_file), len(decks)):
        
        if file_name == decks.iloc[i]['Name']:
            color = s[x].iloc[len(s[x])-2]['Color_type']
            types = s[x].iloc[len(s[x])-1]['Color_type']
            
            if 'W' in color:
                decks.loc[i, 'White'] = 0
            else:
                decks.loc[i, 'White'] = 1
                
            if 'U' in color:
                decks.loc[i, 'Blue'] = 0
            else:
                decks.loc[i, 'Blue'] = 1
                
            if 'B' in color:
                decks.loc[i, 'Black'] = 0
            else:
                decks.loc[i, 'Black'] = 1
                
            if 'R' in color:
                decks.loc[i, 'Red'] = 0
            else:
                decks.loc[i, 'Red'] = 1
                
            if 'G' in color:
                decks.loc[i, 'Green'] = 0
            else:
                decks.loc[i, 'Green'] = 1
                
            
            if 'Agg' in types:
                decks.loc[i, 'Aggro'] = 0
            else:
                decks.loc[i, 'Aggro'] = 1
                
            if 'Mid' in types:
                decks.loc[i, 'Midrange'] = 0
            else:
                decks.loc[i, 'Midrange'] = 1
                
            if 'Con' in types:
                decks.loc[i, 'Control'] = 0
            else:
                decks.loc[i, 'Control'] = 1
                
            if 'Com' in types:
                decks.loc[i, 'Combo'] = 0
            else:
                decks.loc[i, 'Combo'] = 1
                
            if 'Ram' in types:
                decks.loc[i, 'Ramp'] = 0
            else:
                decks.loc[i, 'Ramp'] = 1
                
            
print(decks)

# Making fixes to the dataframe.

# Dataframe int values are floats in some reason so let's convert them back to integers.
convert_points_to_int = {'Victory': int, 'Loss': int, 'Draw': int}
convert_color_to_int = {'White': int, 'Blue': int, 'Black': int, 'Red': int, 'Green': int}
convert_type_to_int = {'Aggro': int, 'Midrange': int, 'Control': int, 'Combo': int, 'Ramp': int}
decks = decks.astype(convert_points_to_int)
decks['Score'] = decks['Score'].astype(float)
decks = decks.astype(convert_color_to_int)
decks = decks.astype(convert_type_to_int)
decks.In_card_data = decks.In_card_data.astype(int)

# For loop adds missing 2022 years to the dates missing the year.
for i in range(len(decks)-len(open_file), len(decks)):
    date = decks.iloc[i]['Date']
    if date[-4:].isdigit() == False:
        decks.loc[i, 'Date'] = date + '2022'
    
    # If '-' is not changed to ',' Excel handles some of the values as dates.
    decks.loc[i, 'Draft_result'] = decks.iloc[i]['Draft_result'].replace('-', ',')
    
# 5 decimals are written to dataframe so excel will not handle them as dates.
for i in range(0, len(decks)):
     decks.loc[i, 'Score'] = format(decks.iloc[i]['Score'], '.5f')

    
print(decks.dtypes)
print(decks)

decks.to_csv('deck_data.csv', sep = ';', index = False) # Saves the deck dataframe to a csv file.



##################




# Initializing dataframes and lists.

# Opening dataframes for future use.
open_file = glob.glob('New_drafts_csv/*')
open_old_file = glob.glob('Drafts_csv/*')
card_data = pd.read_csv('original_card_data.csv', delimiter = ';') # muuta ilman originalia -muotoon
basic_lands = pd.read_csv('original_basic_lands.csv', delimiter = ';')
deck_data = pd.read_csv('deck_data.csv', delimiter = ';')
print(type(deck_data.iloc[3]['Score']))
#deck_data['Score'] = deck_data['Score'].astype(float)
#print(type(deck_data.iloc[3]['Score']))

add_decks, deck_added, old_decks = ([] for i in range(3))
new_file_names, file_names, old_file_names = ([] for i in range(3))

# Checks if the deck is already in the card_data. If not it is added to a list for future use.

for j in range (len(deck_data)):
    if deck_data.iloc[j]['In_card_data'] == 0:
        for i in range(len(open_file)):
            file_name = os.path.basename(open_file[i])
            file_name = os.path.splitext(file_name)[0]
            if file_name == deck_data.iloc[j]['Name']:
                add_decks.append(open_file[i])
                new_file_names.append(file_name)

    else:
        for i in range(len(open_file)):
            file_name = os.path.basename(open_file[i])
            file_name = os.path.splitext(file_name)[0]
            if file_name == deck_data.iloc[j]['Name']:
                deck_added.append(open_file[i])
                file_names.append(file_name)
            
# Saves all files used to create the original card_data dataframe into a list for future use.
for x in range(len(open_old_file)):
    old_decks.append(open_old_file[x])
    file_name = os.path.basename(open_old_file[x])
    old_file_names.append(os.path.splitext(file_name)[0])
    
all_decks = old_decks + deck_added + add_decks # All decks in one list.
all_deck_names = old_file_names + file_names + new_file_names # Names of all decks in one list.

#print(add_decks)
#print(deck_added)
print(old_file_names, '\n')
print(all_deck_names)

print(deck_data['Score'].values)

# Fills the card_data dataframe with names, amounts, main deck count and sideboard count of cards that are not yet in the
# dataframe. Also increases cards' amounts, main deck and sideboard count of cards that are already in the dataframe.
# Also increases the number of lands and amount of decks in the basic_lands dataframe.
    
is_in_cards = 0

for x in range(0, len(add_decks)):
    deck = pd.read_csv(add_decks[x], delimiter = ';')
    deck = deck.astype({'Number_of_card': 'int'})
    
    for i in range(0, len(deck)):
        test_card = deck.iloc[i]['Card_name']
        test_card_amount = deck.at[i, 'Number_of_card']
        
        if (test_card == 'Plains') | (test_card == 'Island') | (test_card == 'Swamp') | (test_card == 'Mountain') | (test_card =='Forest'):
            if deck.iloc[i]['Is_in_sideboard'] == 0:
                if test_card == 'Plains':
                    basic_lands.loc[0, 'Frequency_of_decks'] += 1
                    basic_lands.loc[0, 'Number_of_lands'] += test_card_amount
                
                elif test_card == 'Island':
                    basic_lands.loc[1, 'Frequency_of_decks'] += 1
                    basic_lands.loc[1, 'Number_of_lands'] += test_card_amount
                
                elif test_card == 'Swamp':
                    basic_lands.loc[2, 'Frequency_of_decks'] += 1
                    basic_lands.loc[2, 'Number_of_lands'] += test_card_amount
                
                elif test_card == 'Mountain':
                    basic_lands.loc[3, 'Frequency_of_decks'] += 1
                    basic_lands.loc[3, 'Number_of_lands'] += test_card_amount
                
                else:
                    basic_lands.loc[4, 'Frequency_of_decks'] += 1
                    basic_lands.loc[4, 'Number_of_lands'] += test_card_amount
                
            is_in_cards = 1
        
        else:
            for j in range(0, len(card_data)):
                
                if card_data.iloc[j]['Card_name'] == test_card:
                    card_data.loc[j, 'Frequency_of_cards'] += 1
                    is_in_cards = 1
                    
                    if deck.iloc[i]['Is_in_sideboard'] == 0:
                        card_data.loc[j, 'Main_deck_count'] += 1
                    else:
                        card_data.loc[j, 'Sideboard_count'] += 1
        
        if is_in_cards == 0:
            if deck.iloc[i]['Is_in_sideboard'] == 0:
                new_row = pd.DataFrame({'Card_name': [test_card], 'Frequency_of_cards': [1], 'Main_deck_count': [1],
                                    'Sideboard_count': [0]})
            else:
                new_row = pd.DataFrame({'Card_name': [test_card], 'Frequency_of_cards': [1], 'Main_deck_count': [0],
                                    'Sideboard_count': [1], 'Color': [''], 'Mana_value': [0], 'Type': ['']})

            card_data = pd.concat([card_data, new_row], ignore_index = True, axis = 0)
        is_in_cards = 0
        

# Fills card_data dataframe's Main_deck_rate and Sideboard_rate columns showing just 5 decimals.
for i in range(0, len(card_data)):
    card_data.loc[i, 'Main_deck_rate'] = format((card_data.iloc[i]['Main_deck_count'] / card_data.iloc[i]['Frequency_of_cards']), '.5f')
    card_data.loc[i, 'Sideboard_rate'] = format((card_data.iloc[i]['Sideboard_count'] / card_data.iloc[i]['Frequency_of_cards']), '.5f')

cards_and_their_scores = []

# Fills cards_and_their_scores list with names of the cards and their scores from each deck in deck_data.
for j in range(0, len(deck_data)):
    for x in range(0, len(all_decks)):
        
        if deck_data.iloc[j]['Name'] == all_deck_names[x]:
            deck = pd.read_csv(all_decks[x], delimiter = ';')
            for i in range(0, len(deck)):
                
                if deck.iloc[i]['Is_in_sideboard'] == 0:
                    cards_and_their_scores.append(deck.at[i, 'Card_name'])
                    cards_and_their_scores.append(deck_data.at[j, 'Score'])
                    
                elif deck.iloc[i]['Card_name'] == 'Lutri, the Spellchaser':
                    cards_and_their_scores.append(deck.at[i, 'Card_name'])
                    cards_and_their_scores.append(deck_data.at[j, 'Score'])
            deck_data.loc[j, 'In_card_data'] = 1

print(cards_and_their_scores)

# Calculates point rates for every card based on how well the decks (their been into) succeeded.

score_sum = 0
score_amount = 0

for x in range(0, len(card_data)):
    for i in range(0, len(cards_and_their_scores), 2):
        
        if card_data.iloc[x]['Card_name'] == cards_and_their_scores[i]:
            score_sum += cards_and_their_scores[i+1]
            score_amount += 1
            print(cards_and_their_scores[i+1])
            print(score_sum)
            print(score_amount)
            
    # Must be checked because basic lands are included cards_and_their_scores varible
    if score_amount != 0:
        card_data.loc[x, 'Points_rate'] = score_sum / (score_amount*9)
        
    # If the card has not been in any deck then it's point rate is 0.
    elif score_amount == 0:
        card_data.loc[x, 'Points_rate'] = 0.0

    print(score_sum)
    print(score_amount)
    score_amount = 0
    score_sum = 0
    print(card_data.iloc[x]['Card_name'], ' ', card_data.iloc[x]['Points_rate'])

# Creates a csv files from the basic_lands and cards dataframes.

print(card_data['Points_rate'].values)
print(basic_lands)

deck_data.to_csv('deck_data.csv', sep = ';', index = False)
basic_lands.to_csv('basic_lands.csv', sep = ';', index = False)
card_data.to_csv('card_data.csv', sep = ';', index = False)

print(open_file)



##################




# Initializes variables for getting sum of each color, type or combination of multple colors/types.

# 'original_deck_data.csv'
decks = pd.read_csv('deck_data.csv', delimiter = ';')

# Counters for counting amounts of specified colors and types
white = blue = black = red = green = 0
aggro = midrange = control = combo = ramp = 0

# Counters for counting single color/type decks
w = u = b = r = g = 0
agg = mid = con = com = ram = 0

# Counters for counting decks that have 2 colors
wu = wb = wr = wg = 0
ub = ur = ug = 0
br = bg = rg = 0

# Counters for counting decks that have 2 types
agg_mid = agg_con = agg_com = agg_ramp = 0
mid_con = mid_com = mid_ramp = 0
con_com = con_ramp = com_ramp = 0

# Counters for counting decks that have 3 colors
wub = wur = wug = 0
wbr = wbg = wrg = 0
ubr = ubg = urg = 0
brg = 0

# Counters for counting decks that have 5, 4 or 3 colors or more than 2 types
five_color = four_color = three_color = multi_type =  0


# Initializes lists for saving decks with specific number of color(s)/type(s) per deck.

# esim. kaikki valkoiset voi laskea laskemalla yhteen kaikkien listojen keskiarvot jotka sisältävät valkoista

# 1-5 color decks:

# For loop must be done for lists. With normal variables the above method (var = value) works but not with lists.
mono_w, mono_u, mono_b, mono_r, mono_g = ([] for i in range(5))

twocol_wu, twocol_wb,  twocol_wr, twocol_wg = ([] for i in range(4))
twocol_ub, twocol_ur, twocol_ug = ([] for i in range(3))
twocol_br, twocol_bg, twocol_rg = ([] for i in range(3))

threecol_wub, threecol_wur, threecol_wug = ([] for i in range(3))
threecol_wbr, threecol_wbg, threecol_wrg = ([] for i in range(3))
threecol_ubr, threecol_ubg, threecol_urg = ([] for i in range(3))
threecol_brg = []

# This works also for lists.
fourcol, fivecol = [], []


# 1-5 type decks:

onetype_agg, onetype_mid, onetype_con, onetype_com, onetype_ramp = ([] for i in range(5))

twotype_agg_mid, twotype_agg_con, twotype_agg_com, twotype_agg_ramp = ([] for i in range(4))
twotype_mid_con, twotype_mid_com, twotype_mid_ramp = ([] for i in range(3))
twotype_con_com, twotype_con_ramp, twotype_com_ramp = ([] for i in range(3))

multitype = []

# Calculates average and winrate of scores of all decks. The winrate should be close 50%. (Some missing players
# -> Some players don't have partner for one game so it's considered they won that match -> higher winrate because nobody gets
# 0 points. Also some draws.)

sum_decks = 0
    
for i in range(len(decks)):
    sum_decks += decks.iloc[i]['Score']

average_decks = sum_decks/len(decks)
winrate_dekcs = average_decks/9
    
print(average_decks)
print(winrate_dekcs)

# Initiazes some variables that help to count sums of different colors.
# In for loop the colors of the decks are counted and each deck is added to at least one list based on what color(s) the deck is.
# Saves names of the decks into different lists depending on colors of the decks.

deck_no_color = []

for i in range(0, len(decks)):
    w_count = u_count = b_count = r_count = g_count = 0
    different_c = 0
    
    # Counts how many times the colors appear in decks
    if decks.iloc[i]['White'] == 0:
        white += 1
        w_count = 1
        different_c += 1
        
    if decks.iloc[i]['Blue'] == 0:
        blue += 1
        u_count = 1
        different_c += 1
        
    if decks.iloc[i]['Black'] == 0:
        black += 1
        b_count = 1
        different_c += 1
        
    if decks.iloc[i]['Red'] == 0:
        red += 1
        r_count = 1
        different_c += 1
        
    if decks.iloc[i]['Green'] == 0:
        green += 1
        g_count = 1
        different_c += 1
        
    # If the deck's color is not defined save the deck's name in to a list.
    if different_c == 0:
        deck_no_color.append(decks.loc[i, 'Name'])
    
    # Checks if the deck has only one color.
    if different_c == 1:
        if w_count == 1:
            w += 1
            mono_w.append(decks.loc[i, 'Name'])
            
        elif u_count == 1:
            u += 1
            mono_u.append(decks.loc[i, 'Name'])
            
        elif b_count == 1:
            b += 1
            mono_b.append(decks.loc[i, 'Name'])
            
        elif r_count == 1:
            r += 1
            mono_r.append(decks.loc[i, 'Name'])
            
        else:
            g += 1
            mono_g.append(decks.loc[i, 'Name'])
    
    # Checks if the deck has multiple colors and counts them based on the number of different colors.
    if different_c > 1:
        
        # Calculates how many 3 color decks there exists.
        if different_c == 3:
            three_color += 1
        
        # Calculates how many 5 color decks there exists.
        if different_c > 4:
            five_color += 1
            fivecol.append(decks.loc[i, 'Name'])
            
        # Calculates how many 4 color decks there exists.
        elif different_c > 3:
            four_color += 1
            fourcol.append(decks.loc[i, 'Name'])
        
        # Calculates how many decks that have 2 or 3 colors there exists (for every combination of 2 or 3 types).
        else:
            # if w
            if w_count == 1:
                # if wu
                if u_count == 1:
                    
                    if b_count == 1:
                        wub += 1
                        threecol_wub.append(decks.loc[i, 'Name'])
                        
                    elif r_count == 1:
                        wur += 1
                        threecol_wur.append(decks.loc[i, 'Name'])
                        
                    elif g_count == 1:
                        wug += 1
                        threecol_wug.append(decks.loc[i, 'Name'])
                        
                    else:
                        wu += 1
                        twocol_wu.append(decks.loc[i, 'Name'])
                        
                # if wb
                elif b_count == 1:
                    if r_count == 1:
                        wbr += 1
                        threecol_wbr.append(decks.loc[i, 'Name'])
                        
                    elif g_count == 1:
                        wbg += 1
                        threecol_wbg.append(decks.loc[i, 'Name'])
                        
                    else:
                        wb += 1
                        twocol_wb.append(decks.loc[i, 'Name'])
                        
                # if wr
                elif r_count == 1:
                    if g_count == 1:
                        wrg += 1
                        threecol_wrg.append(decks.loc[i, 'Name'])
                        
                    else:
                        wr += 1
                        twocol_wr.append(decks.loc[i, 'Name'])
                        
                # if wg
                else:
                    wg += 1
                    twocol_wg.append(decks.loc[i, 'Name'])
            
            # if u
            elif u_count == 1:
                # if ub
                if b_count == 1:
                    
                    if r_count == 1:
                        ubr += 1
                        threecol_ubr.append(decks.loc[i, 'Name'])
                        
                    elif g_count == 1:
                        ubg += 1
                        threecol_ubg.append(decks.loc[i, 'Name'])
                        
                    else:
                        ub += 1
                        twocol_ub.append(decks.loc[i, 'Name'])
                        
                # if ur
                elif r_count == 1:
                    if g_count == 1:
                        urg += 1
                        threecol_urg.append(decks.loc[i, 'Name'])
                        
                    else:
                        ur += 1
                        twocol_ur.append(decks.loc[i, 'Name'])
                        
                # if ug
                else:
                    ug += 1
                    twocol_ug.append(decks.loc[i, 'Name'])
                
            # if b
            elif b_count == 1:
                # if br
                if r_count == 1:
                    
                    if g_count == 1:
                        brg += 1
                        threecol_brg.append(decks.loc[i, 'Name'])
                        
                    else:
                        br += 1
                        twocol_br.append(decks.loc[i, 'Name'])
                        
                # if bg
                else:
                    bg += 1
                    twocol_bg.append(decks.loc[i, 'Name'])
                    
            # if rg
            else:
                rg += 1
                twocol_rg.append(decks.loc[i, 'Name'])


print('These decks dont have color:\n', deck_no_color)
print('Total number of\n White {}, Blue {}, Black {}, Red {}, Green {} decks\n'.format(white, blue, black, red, green))
print('Number of mono\n White {}, Blue {}, Black {}, Red {}, Green {} decks\n'.format(w, u, b, r, g))
print('Amount of different decks having 2 different colors:\n wu {}, wb {}, wr {}, wg {}, ub {}, ur {}, ug {}, br {}, bg {}, rg {}\n'.format(wu, wb, wr, wg, ub, ur, ug, br, bg, rg))
print('Amount of different decks having 3 different colors:\n wub {}, wur {}, wug {}, wbr {}, wbg {}, wrg {}, ubr {}, ubg {}, urg {}, brg {}\n'.format(wub, wur, wug, wbr, wbg, wrg, ubr, ubg, urg, brg))
print('Amount of 3 color decks: {}\n'.format(three_color))
print('Amount of 4 color decks: {}\n'.format(four_color))
print('Amount of 5 color decks: {}\n'.format(five_color))
print('Total number of decks: ', len(decks))
#print(twocol_rg)

# Initiazes a variable that helps to count sums of different types.
# In for loop the types of the decks are counted and each deck is added to at least one list based on what type(s) the deck is.
# Saves names of the decks into different lists depending on types of the decks.

deck_no_type = []

for i in range(0, len(decks)):
    agg_count = mid_count = con_count = com_count = ra_count = 0
    different_t = 0
    
    # Counts how many times the types appear in decks
    if decks.iloc[i]['Aggro'] == 0:
        aggro += 1
        agg_count = 1
        different_t += 1
        
    if decks.iloc[i]['Midrange'] == 0:
        midrange += 1
        mid_count = 1
        different_t += 1
        
    if decks.iloc[i]['Control'] == 0:
        control += 1
        con_count = 1
        different_t += 1
        
    if decks.iloc[i]['Combo'] == 0:
        combo += 1
        com_count = 1
        different_t += 1
        
    if decks.iloc[i]['Ramp'] == 0:
        ramp += 1
        ra_count = 1
        different_t += 1
        
    # If the deck's type is not defined save the deck's name in to a list.
    if different_t == 0:
        deck_no_type.append(decks.loc[i, 'Name'])
    
    # Checks if the deck has only one type.
    if different_t == 1:
        if agg_count == 1:
            agg += 1
            onetype_agg.append(decks.loc[i, 'Name'])
            
        elif mid_count == 1:
            mid += 1
            onetype_mid.append(decks.loc[i, 'Name'])
            
        elif con_count == 1:
            con += 1
            onetype_con.append(decks.loc[i, 'Name'])
            
        elif com_count == 1:
            com += 1
            onetype_com.append(decks.loc[i, 'Name'])
            
        else:
            ram += 1
            onetype_ramp.append(decks.loc[i, 'Name'])
    
    # Checks if the deck has multiple types and counts them based on the number of different types.
    if different_t > 1:
        
        # Calculates how many decks that have 3 or more types there exists.
        if different_t > 2:
            multi_type += 1
            multitype.append(decks.loc[i, 'Name'])
        
        # Calculates how many decks that have 2 types there exists (for every combination of 2 types).
        else:
            # if aggro
            if agg_count == 1:
                
                # if aggro-midrange
                if mid_count == 1:
                    agg_mid += 1
                    twotype_agg_mid.append(decks.loc[i, 'Name'])
                        
                # if aggro-control
                elif con_count == 1:
                    agg_con += 1
                    twotype_agg_con.append(decks.loc[i, 'Name'])
                        
                # if aggro-combo
                elif com_count == 1:
                    agg_com += 1
                    twotype_agg_com.append(decks.loc[i, 'Name'])
                        
                # if aggro-ramp
                else:
                    agg_ramp += 1
                    twotype_agg_ramp.append(decks.loc[i, 'Name'])
            
            # if midrange
            elif mid_count == 1:
                # if midrange-control
                if con_count == 1:
                    mid_con += 1
                    twotype_mid_con.append(decks.loc[i, 'Name'])
                        
                # if midrange-combo
                elif com_count == 1:
                    mid_com += 1
                    twotype_mid_com.append(decks.loc[i, 'Name'])
                        
                # if midrange-ramp
                else:
                    mid_ramp += 1
                    twotype_mid_ramp.append(decks.loc[i, 'Name'])
                
            # if control
            elif con_count == 1:
                # if control-combo
                if com_count == 1:
                    con_com += 1
                    twotype_con_com.append(decks.loc[i, 'Name'])
                    
                # if control-ramp
                else:
                    con_ramp += 1
                    twotype_con_ramp.append(decks.loc[i, 'Name'])
                        
            # Else combo-ramp
            else:
                com_ramp += 1
                twotype_com_ramp.append(decks.loc[i, 'Name'])

print('These decks dont have type:\n', deck_no_type)
print('Total number of\n Aggro {}, Midrange {}, Control {}, Combo {}, Ramp {} decks\n'.format(aggro, midrange, control, combo, ramp))
print('Number of\n Aggro {}, Midrange {}, Control {}, Combo {}, Ramp {} decks\n'.format(agg, mid, con, com, ram))
print('Amount of different decks having 2 different types:\n agg_mid {}, agg_con {}, agg_com {}, agg_ramp {}, mid_con {}, mid_com {}, mid_ramp {}, con_com {}, con_ramp {}, com_ramp {}\n'.format(agg_mid, agg_con, agg_com, agg_ramp, mid_con, mid_com, mid_ramp, con_com, con_ramp, com_ramp))
print('Amount of decks having over 2 different types/total number of decks: {}/{}'.format(multi_type, len(decks)))

# Creates 2 dataframes: one for winrates of colors and the other one for winrates of types.
# First creates 3 lists: one with color/type names, second and third with zeros. Then the dataframe is created using the 3 lists.

color_list = ['W', 'U', 'B', 'R', 'G', 'WU', 'WB', 'WR', 'WG', 'UB', 'UR', 'UG', 'BR', 'BG', 'RG', 'WUB', 'WUR', 'WUG', 'WBR', 'WBG', 'WRG', 'UBR', 'UBG', 'URG', 'BRG', '4 color', '5 color']
average_points_c = [0 for i in range(len(color_list))]
winrates_c = [0 for j in range(len(color_list))]

color_winrate_data = pd.DataFrame(list(zip(color_list, average_points_c, winrates_c)) , columns = ['Color', 'Average_points', 'Winrate'])

type_list = ['Aggro', 'Midrange', 'Control', 'Combo', 'Ramp', 'Aggro Mid', 'Aggro Con', 'Aggro Combo', 'Aggro Ramp', 'Mid Control', 'Mid Combo', 'Mid Ramp', 'Control Combo', 'Control Ramp', 'Combo Ramp', 'over 2 types']
average_points_t = [0 for i in range(len(type_list))]
winrates_t = [0 for j in range(len(type_list))]

type_winrate_data = pd.DataFrame(list(zip(type_list, average_points_t, winrates_t)) , columns = ['Type', 'Average_points', 'Winrate'])

# Function for calculating winrates of the specific decks based on color(s). for example mono red (Only red color cards in deck. 
# May contain colorless cards.) or red and green deck.
# First checks if there are any decks with specific color(s) and when that's true the sums of points of the decks are calculated.
# Then the average of the points is calculated and after that the winrate (how often the deck has won).
# Last all winrates for specified color combinations are counted.

def winrate_color(colorList, string, x):
    summary = 0
    if len(colorList) > 0:
        for i in range(0, len(colorList)):
            for j in range(0, len(decks)):
                if colorList[i] == decks.iloc[j]['Name']:
                    summary += decks.loc[j, 'Score']

        average = summary/len(colorList)
        winrate = average/9 # 9 is max points what can be get (3 opponents, 3 win)
        
    else:
        average = 0
        winrate = 0
        
    print(string, colorList)
    print('Average points', average)
    print('Winrate', format(winrate, '.4f'), '%\n')
    color_winrate_data.loc[x, 'Average_points'] = average
    color_winrate_data.loc[x, 'Winrate'] = format(winrate, '.5f')
        
winrate_color(mono_w, 'W: ', 0)
winrate_color(mono_u, 'U: ', 1)
winrate_color(mono_b, 'B: ', 2)
winrate_color(mono_r, 'R: ', 3)
winrate_color(mono_g, 'G: ', 4)


winrate_color(twocol_wu, 'WU: ', 5)
winrate_color(twocol_wb, 'WB: ', 6)
winrate_color(twocol_wr, 'WR: ', 7)
winrate_color(twocol_wg, 'WG: ', 8)

winrate_color(twocol_ub, 'UB: ', 9)
winrate_color(twocol_ur, 'UR: ', 10)
winrate_color(twocol_ug, 'UG: ', 11)

winrate_color(twocol_br, 'BR: ', 12)
winrate_color(twocol_bg, 'BG: ', 13)
winrate_color(twocol_rg, 'RG: ', 14)


winrate_color(threecol_wub, 'WUB: ', 15)
winrate_color(threecol_wur, 'WUR: ', 16)
winrate_color(threecol_wug, 'WUG: ', 17)
winrate_color(threecol_wbr, 'WBR: ', 18)
winrate_color(threecol_wbg, 'WBG: ', 19)
winrate_color(threecol_wrg, 'WRG: ', 20)

winrate_color(threecol_ubr, 'UBR: ', 21)
winrate_color(threecol_ubg, 'UBG: ', 22)
winrate_color(threecol_urg, 'URG: ', 23)
winrate_color(threecol_brg, 'BRG: ', 24)

winrate_color(fourcol, '4 color: ', 25)
winrate_color(fivecol, '5 color: ', 26)

# Counting winrates for all decks that have the same specific color (ignoring if there is another color with it or not).
# First counts summaries and amounts of specific color (e.g. counts how many decks are white decks and 
# counts sums of their average points). Then counts averages and winrates and saves them into dataframe of the types.

averlist_w, averlist_u, averlist_b, averlist_r, averlist_g = ([] for i in range(5))
amountlist_w = [w, wu, wb, wr, wg, wub, wur, wug, wbr, wbg, wrg]
amountlist_u = [u, wu, ub, ur, ug, wub, wur, wug, ubr, ubg, urg]
amountlist_b = [b, wb, ub, br, bg, wub, wbr, wbg, ubr, ubg, brg]
amountlist_r = [r, wr, ur, br, rg, wur, wbr, wrg, ubr, urg, brg]
amountlist_g = [g, wg, ug, bg, rg, wug, wbg, wrg, ubg, urg, brg]

for i in range(len(color_winrate_data)):
    
    if 'W' in color_winrate_data.iloc[i]['Color']:
        averlist_w.append(color_winrate_data.iloc[i]['Average_points'])
        
    if 'U' in color_winrate_data.iloc[i]['Color']:
        averlist_u.append(color_winrate_data.iloc[i]['Average_points'])
        
    if 'B' in color_winrate_data.iloc[i]['Color']:
        averlist_b.append(color_winrate_data.iloc[i]['Average_points'])
        
    if 'R' in color_winrate_data.iloc[i]['Color']:
        averlist_r.append(color_winrate_data.iloc[i]['Average_points'])
    
    if 'G' in color_winrate_data.iloc[i]['Color']:
        averlist_g.append(color_winrate_data.iloc[i]['Average_points'])

def all_color_winrate(color, averlist, amountlist):
    summary = 0
    amount = 0
    
    for i in range(len(averlist)):
        summary += averlist[i]*amountlist[i]
    
    amount = sum(amountlist)
    average = summary/amount
    winrate = average/9
    
    color_winrate_data.loc[len(color_winrate_data['Color']), 'Color'] = 'All ' + color
    color_winrate_data.loc[len(color_winrate_data['Color'])-1, 'Average_points'] = average
    color_winrate_data.loc[len(color_winrate_data['Color'])-1, 'Winrate'] = format(winrate, '.5f')

all_color_winrate('whites', averlist_w, amountlist_w)
all_color_winrate('blues', averlist_u, amountlist_u)
all_color_winrate('blacks', averlist_b, amountlist_b)
all_color_winrate('reds', averlist_r, amountlist_r)
all_color_winrate('greens', averlist_g, amountlist_g)

print(color_winrate_data)

# Function for calculating winrates of the specific decks based on type(s). For example aggro deck (Deck's strategy is being aggressive.)
# or aggro midrange deck (Midrange deck which strategy is to be somewhat aggressive rather than defensive).
# First checks if there are any decks with specific type(s) and when that's true the sums of points of the decks are calculated.
# Then the average of the points is calculated and after that the winrate (how often the deck has won).
# Last all winrates for specified type combinations are counted.

def winrate_type(typeList, string, x):
    summary = 0
    if len(typeList) > 0:
        for i in range(0, len(typeList)):
            for j in range(0, len(decks)):
                if typeList[i] == decks.iloc[j]['Name']:
                    summary += decks.loc[j, 'Score']

        average = summary/len(typeList)
        winrate = average/9 # 9 is max points what can be get (3 opponents, 3 win)
        
    else:
        average = 0
        winrate = 0
        
    print(string, typeList)
    print('Average points', average)
    print('Winrate', format(winrate, '.4f'), '%\n')
    type_winrate_data.loc[x, 'Average_points'] = average
    type_winrate_data.loc[x, 'Winrate'] = format(winrate, '.5f')

winrate_type(onetype_agg, 'Aggro: ', 0)
winrate_type(onetype_mid, 'Mid: ', 1)
winrate_type(onetype_con, 'Control: ', 2)
winrate_type(onetype_com, 'Combo: ', 3)
winrate_type( onetype_ramp, 'Ramp: ', 4)


winrate_type(twotype_agg_mid, 'Aggro Mid: ', 5)
winrate_type(twotype_agg_con, 'Aggro Control: ', 6)
winrate_type(twotype_agg_com, 'Aggro Combo: ', 7)
winrate_type(twotype_agg_ramp, 'Aggro Ramp: ', 8)

winrate_type(twotype_mid_con, 'Mid Control: ', 9)
winrate_type(twotype_mid_com, 'Mid Combo: ', 10)
winrate_type(twotype_mid_ramp, 'Mid Ramp: ', 11)

winrate_type(twotype_con_com, 'Control Combo: ', 12)
winrate_type(twotype_con_ramp, 'Control Ramp: ', 13)
winrate_type(twotype_com_ramp, 'Combo Ramp: ', 14)

print()
winrate_type(multitype, 'At least 3 different types: ', 15)

# Counting winrates for all decks that have the same specific type (ignoring if there is another type with it or not).
# First counts summaries and amounts of specific type (e.g. counts how many decks are aggro decks and 
# counts sums of their average points). Then counts averages and winrates and saves them into dataframe of the types.

averlist_agg, averlist_mid, averlist_con, averlist_com, averlist_ramp = ([] for i in range(5))
amountlist_agg = [agg, agg_mid, agg_con, agg_com, agg_ramp]
amountlist_mid = [mid, agg_mid, mid_con, mid_com, mid_ramp]
amountlist_con = [con, agg_con, mid_con, con_com, con_ramp]
amountlist_com = [com, agg_com, mid_com, con_com, com_ramp]
amountlist_ramp = [ramp, agg_ramp, mid_ramp, con_ramp, com_ramp]

for i in range(len(type_winrate_data)):
    
    if 'Aggro' in type_winrate_data.iloc[i]['Type']:
        averlist_agg.append(type_winrate_data.iloc[i]['Average_points'])
        
    if 'Mid' in type_winrate_data.iloc[i]['Type']:
        averlist_mid.append(type_winrate_data.iloc[i]['Average_points'])
        
    if 'Control' in type_winrate_data.iloc[i]['Type']:
        averlist_con.append(type_winrate_data.iloc[i]['Average_points'])
        
    if 'Combo' in type_winrate_data.iloc[i]['Type']:
        averlist_com.append(type_winrate_data.iloc[i]['Average_points'])
    
    if 'Ramp' in type_winrate_data.iloc[i]['Type']:
        averlist_ramp.append(type_winrate_data.iloc[i]['Average_points'])
        
def all_type_winrate(types, averlist, amountlist):
    summary = 0
    amount = 0
    
    for i in range(len(averlist)):
        summary += averlist[i]*amountlist[i]
    
    amount = sum(amountlist)
    average = summary/amount
    winrate = average/9
    
    type_winrate_data.loc[len(type_winrate_data['Type']), 'Type'] = 'All ' + types
    type_winrate_data.loc[len(type_winrate_data['Type'])-1, 'Average_points'] = average
    type_winrate_data.loc[len(type_winrate_data['Type'])-1, 'Winrate'] = format(winrate, '.5f')

all_type_winrate('aggros', averlist_agg, amountlist_agg)
all_type_winrate('mids', averlist_mid, amountlist_mid)
all_type_winrate('controls', averlist_con, amountlist_con)
all_type_winrate('combos', averlist_com, amountlist_com)
all_type_winrate('ramps', averlist_ramp, amountlist_ramp)

print(type_winrate_data)

# Saves only 5 decimals to average points of dataframes and then creates csv files from dataframes.

for i in range(len(color_winrate_data)):
    color_winrate_data.loc[i, 'Average_points'] = format(float(color_winrate_data.iloc[i]['Average_points']), '.5f')
    
for i in range(len(type_winrate_data)):
    type_winrate_data.loc[i, 'Average_points'] = format(float(type_winrate_data.iloc[i]['Average_points']), '.5f')

# 'original_color_data.csv', 'original_type_data.csv'
color_winrate_data.to_csv('color_data.csv', sep = ';', index = False)
type_winrate_data.to_csv('type_data.csv', sep = ';', index = False)



##################




# Initializing dataframes and a list.

card_data = pd.read_csv('card_data.csv', delimiter = ';')
new_cards = []
new_cards_ff = pd.DataFrame()

# Saves rows that have have Null value in Color column to new_cards_ff dataframe. This dataframe will be filled and used to 
# add missing features to card_data later on. Unnecessary columns are deleted form new_cards_ff.

new_row = pd.isnull(card_data['Color'])
new_cards_ff = card_data[new_row]
new_cards_ff = new_cards_ff.drop(columns = ['Frequency_of_cards', 'Main_deck_count', 'Sideboard_count', 'Main_deck_rate', 'Sideboard_rate', 'Points_rate'])

print(new_cards_ff)

new_cards_ff.to_csv('cards_ff.csv', sep = ';', index = False) # Saves changes of dataframe to csv file.



##################




# Initializing dataframes.

card_data = pd.read_csv('card_data.csv', delimiter = ';')
cards_ff = pd.read_csv('cards_ff.csv', delimiter = ';')

# Fills empty feature columns with values from cards_fill_features dataframe. If a value is not found to a specific card name
# print the name of the card.

for i in range(len(card_data)):
    for j in range(len(cards_ff)):
        
        if card_data.iloc[i]['Card_name'] == cards_ff.iloc[j]['Card_name']:
            card_data.loc[i, 'Color'] = cards_ff.iloc[j]['Color']
            card_data.loc[i, 'Mana_value'] = cards_ff.iloc[j]['Mana_value']
            card_data.loc[i, 'Type'] = cards_ff.iloc[j]['Type']

print(card_data)

card_data.to_csv('card_data.csv', sep = ';', index = False) # Saves changes of dataframe to csv file.



##################



# The point of this code section is create a csv that can be used more easier to any kind of purposes to use colors and types of cards.
# The non-copy version, card_data.csv, is more suitable for humans to read but not in code purposes.


# Initializing dataframes and columns for one of them. Also removes spaces from the beginnings and the endings of the 
# strings in Type column in card_data dataframe.

card_data = pd.read_csv('card_data.csv', delimiter = ';')

for i in range(len(card_data)):
    card_data.loc[i, 'Type'] = card_data.iloc[i]['Type'].strip()

    
analysis_card_data = card_data.copy()
analysis_card_data[['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless']] = 1

print(analysis_card_data)

# Initializes columns from different card types for analysis_card_data dataframe.
# First creates columns from one type values and then checks if there's any type left in multiple type values that's not already
# made to a column. If there's a type that's not already a column, a new column will be created that's carrying the name of 
# the type.

uniq_types = card_data['Type'].value_counts().index.tolist()
one_type = []

for i in range(len(uniq_types)):
    if ' ' not in uniq_types[i]:
        analysis_card_data[uniq_types[i]] = 1
        one_type.append(uniq_types[i])
        
for i in range(len(uniq_types)):
    if ' ' in uniq_types[i]:
        string1, string2 = uniq_types[i].split()
        # "+" doesn't put space between string and "','" but "','," puts space between "','" and string in print
        print(string1 + ',', string2)
        
        if string1 not in one_type:
            analysis_card_data[string1] = 1
            one_type.append(string1)
            print('string1')
            
        elif string2 not in one_type:
            analysis_card_data[string2] = 1
            print('string2')

print(analysis_card_data.iloc[:, 16:])

# Fills created columns with values got from columns Type and Color. For example if a card is white it contains 'W' in Color.
# If so then White column gets value 0 for white been at least one of the colors of the card.

for i in range(len(analysis_card_data)):
    if 'W' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'White'] = 0
        
    if 'U' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'Blue'] = 0
        
    if 'B' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'Black'] = 0
        
    if 'R' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'Red'] = 0
        
    if 'G' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'Green'] = 0
    
    if 'Colorless' in analysis_card_data.iloc[i]['Color']:
        analysis_card_data.loc[i, 'Colorless'] = 0
        
    if 'Creature' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Creature'] = 0
        
    if 'Land' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Land'] = 0
        
    if 'Sorcery' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Sorcery'] = 0
        
    if 'Instant' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Instant'] = 0
        
    if 'Artifact' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Artifact'] = 0
    
    if 'Planeswalker' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Planeswalker'] = 0
    
    if 'Enchantment' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Enchantment'] = 0
        
    if 'Tribal' in analysis_card_data.iloc[i]['Type']:
        analysis_card_data.loc[i, 'Tribal'] = 0
        
print(analysis_card_data.iloc[:100, 10:])

analysis_card_data = analysis_card_data.drop(analysis_card_data[['Color', 'Type']], axis = 1) # Deletes unnecessary columns.

analysis_card_data.to_csv('analysis_card_data.csv', sep = ';', index = False) # Saves the deck dataframe to a csv file.



##################




# Initializing dataframes.
card_data = pd.read_csv('card_data.csv', delimiter = ';')
#card_types = pd.DataFrame({'Type': ['Creature'], 'Amount': [0]})
#card_types['Type'] = 

# If type ends ' ' replace it with ''

for i in range(len(card_data)):
    card_data.loc[i, 'Type'] = card_data.iloc[i]['Type'].strip() # Removes spaces from the beginning and the ending of the string.

#type_count = card_data['Type'].value_counts() # Counts the amount of values of different types.
#uniq_types = card_data['Type'].value_counts().index.tolist() # Creates a list of different types.

#print(uniq_types)
#print(type_count)


card_data.to_csv('card_data.csv', sep = ';', index = False) # Saves changes of dataframe to csv file.
