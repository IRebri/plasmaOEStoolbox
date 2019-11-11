# myconfig.py:
# e.g. rastr = (67, 113) = last (x,y) from kud_df

raw_Kud = "spec_scan_2019_10_10__13-18-06.txt"
raw_Mal = "MPMA_20191010131801.txt"
my_fname = "__118_13_18_"
rastr = (55,99) # -1 from photo 
tsync = 5 # bigger tsync moves bad-line to the top
#such coefficient in {mal_df['time'] = mal_df['time'] - 20.0 + tsync*0.25} where 20.0 comes from
#15-41-17.08 (kud_df) and 15-40-57 (mal file name) ->20.0