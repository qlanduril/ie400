from gurobipy import Model, GRB, quicksum

def main():

    # Create a new model
    model = Model("MusicModel")

    # Decision variables
    artists = ["Far Eastern", "Higher Days", "Mark A Day", "Steps Away", "The Filaments", "Toni Travis"]
    genres = ["Country", "EDM", "Folk", "Hip Hop", "Pop", "Rock"]
    songs = ["All For Love", "Ceiling", "Dear Daisy", "Heaven", "On The Edge", "Seven Years"]
    lengths = ["2:34", "2:58", "3:12", "3:36", "4:00", "4:14"]

    # Helper function to convert time strings to total seconds
    def time_to_seconds(t):
        min, sec = map(int, t.split(':'))
        return min * 60 + sec

    # Create variables
    # artist_genre_song_length[artist][genre][song][length]
    x = model.addVars(artists, genres, songs, lengths, vtype=GRB.BINARY, name="x")
    
    # Ensuring that each artist is associated with exactly one genre, song, and length
    for artist in artists:
        model.addConstr(quicksum(x[artist, genre, song, length] for genre in genres for song in songs for length in lengths) == 1, f"Artist_{artist}")

    # Ensure that each song is associated with exactly one artist, genre, and length
    for genre in genres:
        model.addConstr(quicksum(x[artist, genre, song, length] for artist in artists for song in songs for length in lengths) == 1, f"Genre_{genre}")

    # Ensure that each genre is associated with exactly one artist, song, and length
    for song in songs:
        model.addConstr(quicksum(x[artist, genre, song, length] for artist in artists for genre in genres for length in lengths) == 1, f"Song_{song}")

    # Ensure that each length is associated with exactly one artist, song, and genre
    for length in lengths:
        model.addConstr(quicksum(x[artist, genre, song, length] for artist in artists for genre in genres for song in songs) == 1, f"Length_{length}")
      
    # Constraints
    
    
    # Constraint 1 ------------
    # The six songs are the one by Higher Days, the one that goes for exactly 2 minutes 34 seconds, 
    # "Ceiling", "Seven Years", the one by Mark A Day, and the EDM track.
    
    # Artist "Higher Days" canot have "Ceiling" or "Seven Years" as a song
    model.addConstr(quicksum(x["Higher Days", j, "Ceiling", l] for j in genres for l in lengths) == 0, "Higher_Days_not_Ceiling")
    model.addConstr(quicksum(x["Higher Days", j, "Seven Years", l] for j in genres for l in lengths) == 0, "Higher_Days_not_Seven_Years")
    
    # Artist "Higher Days" cannot have a song that is 2:34 long
    model.addConstr(quicksum(x["Higher Days", j, k, "2:34"] for j in genres for k in songs) == 0, "Higher_Days_not_2_34")
    
    # Artist "Higher Days" cannot have a song in EDM genre
    model.addConstr(quicksum(x["Higher Days", "EDM", k, l] for k in songs for l in lengths) == 0, "Higher_Days_not_EDM")
    
    # Artist "Mark A Day" canot have "Ceiling" or "Seven Years" as a song
    model.addConstr(quicksum(x["Mark A Day", j, "Ceiling", l] for j in genres for l in lengths) == 0, "Mark_A_Day_not_Ceiling")
    model.addConstr(quicksum(x["Mark A Day", j, "Seven Years", l] for j in genres for l in lengths) == 0, "Mark_A_Day_not_Seven_Years")
    
    # Artist "Mark A Day" cannot have a song that is 2:34 long
    model.addConstr(quicksum(x["Mark A Day", j, k, "2:34"] for j in genres for k in songs) == 0, "Mark_A_Day_not_2_34")
    
    # Artist "Mark A Day" cannot have a song in EDM genre
    model.addConstr(quicksum(x["Mark A Day", "EDM", k, l] for k in songs for l in lengths) == 0, "Mark_A_Day_not_EDM")
    
            
    # "Ceiling" and "Seven Years" cannot be 2:34 long
    model.addConstr(quicksum(x[artist, genre, "Ceiling", "2:34"] for artist in artists for genre in genres) == 0, "Ceiling_not_2_34")
    model.addConstr(quicksum(x[artist, genre, "Seven Years", "2:34"] for artist in artists for genre in genres) == 0, "Seven_Years_not_2_34")
            

    # "Ceiling" and "Seven Years" cannot be EDM genre    
    model.addConstr(quicksum(x[i, "EDM", "Ceiling", l] for i in artists for l in lengths) == 0, "Ceiling_not_EDM")
    model.addConstr(quicksum(x[i, "EDM", "Seven Years", l] for i in artists for l in lengths) == 0, "Seven_Years_not_EDM")
    

    # Constraint 2 ------------
    # Of "Dear Daisy" and the song by Mark A Day, one is 3:36 long and the other is a Pop song.  
    dear_daisy_3_36 = quicksum(x[artist, genre, "Dear Daisy", "3:36"] for artist in artists for genre in genres)
    dear_daisy_pop = quicksum(x[artist, "Pop", "Dear Daisy", length] for artist in artists for length in lengths)
    
    mark_a_day_pop = quicksum(x["Mark A Day", "Pop", song, length] for song in songs for length in lengths)
    mark_a_day_3_36 = quicksum(x["Mark A Day", genre, song, "3:36"] for genre in genres for song in songs)
    
    model.addConstr(dear_daisy_3_36 + dear_daisy_pop == 1, "dear_daisy_3_36_pop")
    model.addConstr(mark_a_day_3_36 + mark_a_day_pop == 1, "mark_a_day_3_36_pop")
    model.addConstr(dear_daisy_3_36 + mark_a_day_3_36 == 1, "dear_daisy_mark_a_day_3_36")     
    

    # Constraint 3 ------------
    # "On The Edge" plays for longer than Toni Travis’s track
    model.addConstr(quicksum(time_to_seconds(length) * x[artist, genre, "On The Edge", length] for artist in artists for genre in genres for length in lengths) >= 
                    quicksum(time_to_seconds(length) * x["Toni Travis", genre, song, length] for genre in genres for song in songs for length in lengths),
                    "on_the_edge_longer_than_toni")
                
    # Constraint 4 ------------
    # The Country song has a shorter duration than Steps Away’s offering.
    model.addConstr(quicksum(time_to_seconds(length) * x[artist, "Country", song, length] for artist in artists for song in songs for length in lengths) <= 
                    quicksum(time_to_seconds(length) * x["Steps Away", genre, song, length] for genre in genres for song in songs for length in lengths),
                    "country_shorter_than_steps_away")
    
    # Constraint 5 ------------
    # It’s no accident that "On The Edge" is precisely 4 minutes long, with the artist being a fan of round numbers
    model.addConstr(quicksum(x[artist, genre, "On The Edge", "4:00"] for artist in artists for genre in genres) == 1, "on_the_edge_4_minutes")
    
    # Constraint 6 ------------
    # No song starts with the first letter of its artist’s name.
    for artist in artists:
        for song in songs:
            artist_first_letter = artist[0].lower()
            song_first_letter = song[0].lower()
            
            is_possible = int(artist_first_letter != song_first_letter)
            
            model.addConstr(sum(x[artist, genre, song, length] for genre in genres for length in lengths) <= is_possible, f"no_song_starts_with_first_letter_{artist}_{song}")
                    
    # Constraint 7 ------------
    # Of "Ceiling" and the Higher Days song, one is a Folk song and the other is 2:58 long.
    sum_ceiling_2_58 = quicksum(x[artist, genre, "Ceiling", "2:58"] for artist in artists for genre in genres)
    sum_ceiling_folk = quicksum(x[artist, "Folk", "Ceiling", length] for artist in artists for length in lengths)
    
    sum_higher_days_2_58 = quicksum(x["Higher Days", genre, song, "2:58"] for genre in genres for song in songs)
    sum_higher_days_folk = quicksum(x["Higher Days", "Folk", song, length] for song in songs for length in lengths)
            
    model.addConstr(sum_ceiling_2_58 + sum_ceiling_folk == 1, "ceiling_2_58_folk")
    model.addConstr(sum_higher_days_2_58 + sum_higher_days_folk == 1, "higher_days_2_58_folk")
    model.addConstr(sum_ceiling_2_58 + sum_higher_days_2_58 == 1, "ceiling_higher_days_2_58")
    

    # Constraint 8 ------------
    # There is a difference in duration of 1 minute 2 seconds between the Hip Hop song and the song by The Filaments.
    hip_hop_duration = quicksum(time_to_seconds(length) * x[artist, "Hip Hop", song, length] for artist in artists for song in songs for length in lengths)
    filaments_duration = quicksum(time_to_seconds(length) * x["The Filaments", genre, song, length] for genre in genres for song in songs for length in lengths)

    # Difference in duration
    d = model.addVar(vtype=GRB.INTEGER, name="duration_difference")
    pos_diff = model.addVar(vtype=GRB.BINARY, name="pos_diff")
    neg_diff = model.addVar(vtype=GRB.BINARY, name="neg_diff")

    # Set the relationship between d, pos_diff, and neg_diff
    model.addConstr(d == hip_hop_duration - filaments_duration, "duration_diff_def")
    model.addConstr(d == 62 * pos_diff - 62 * neg_diff, "abs_diff_62_seconds")

    # Ensure only one of pos_diff or neg_diff is true (logical exclusive OR)
    model.addConstr(pos_diff + neg_diff == 1, "xor_pos_neg_diff")
    
    # Constraint 9 ------------
    # • The Rock song is 14 seconds longer than the Country song.
    model.addConstr(quicksum(time_to_seconds(length) * x[artist, "Rock", song, length] for artist in artists for song in songs for length in lengths) ==
                    quicksum(time_to_seconds(length) * x[artist, "Country", song, length] for artist in artists for song in songs for length in lengths) + 14, "rock_14_seconds_longer_than_country")
    
    # Constraint 10 ------------
    # • Far Eastern’s song is 24 seconds longer than "Heaven".
    model.addConstr(quicksum(time_to_seconds(length) * x["Far Eastern", genre, song, length] for genre in genres for song in songs for length in lengths) ==
                    quicksum(time_to_seconds(length) * x[artist, genre, "Heaven", length] for artist in artists for genre in genres for length in lengths) + 24, "far_eastern_24_seconds_longer_than_heaven")
    
    # Constraint 11 ------------
    # "Dear Daisy" is not Hip Hop nor Folk
    model.addConstr(quicksum(x[artist, "Hip Hop", "Dear Daisy", length] for artist in artists for length in lengths) == 0, "dear_daisy_not_hip_hop")
    model.addConstr(quicksum(x[artist, "Folk", "Dear Daisy", length] for artist in artists for length in lengths) == 0, "dear_daisy_not_folk")
    
    # Constraint 12 ------------
    # Far Eastern’s song is longer than the Pop song, but shorter than Steps Away’s song.
    model.addConstr(quicksum(x["Far Eastern", "Pop", song, length] for song in songs for length in lengths) == 0, "far_eastern_not_pop")
    
    model.addConstr(quicksum(time_to_seconds(length) * x["Far Eastern", genre, song, length] for genre in genres for song in songs for length in lengths) >= 
                    quicksum(time_to_seconds(length) * x[artist, "Pop", song, length] for artist in artists for song in songs for length in lengths), 
                    "far_eastern_longer_than_pop")
    
    model.addConstr(quicksum(time_to_seconds(length) * x["Far Eastern", genre, song, length] for genre in genres for song in songs for length in lengths) <= 
                    quicksum(time_to_seconds(length) * x["Steps Away", genre, song, length] for genre in genres for song in songs for length in lengths), "far_eastern_shorter_than_steps_away")
    
    # Constraint 13 ------------
    # "All For Love", which is not a Hip Hop song, was not recorded by The Filaments, Toni Travis, nor Mark A Day.
    model.addConstr(quicksum(x[artist, "Hip Hop", "All For Love", length] for artist in artists for length in lengths) == 0, "all_for_love_not_hip_hop")
    model.addConstr(quicksum(x["The Filaments", genre, "All For Love", length] for genre in genres for length in lengths) == 0, "all_for_love_not_the_filaments")
    model.addConstr(quicksum(x["Toni Travis", genre, "All For Love", length] for genre in genres for length in lengths) == 0, "all_for_love_not_toni_travis")
    model.addConstr(quicksum(x["Mark A Day", genre, "All For Love", length] for genre in genres for length in lengths) == 0, "all_for_love_not_mark_a_day")
    

    # Optimize model
    model.optimize()

    # Output solution
    if model.status == GRB.OPTIMAL:
        for artist in artists:
            for genre in genres:
                for song in songs:
                    for length in lengths:
                        if x[artist, genre, song, length].X > 0.5:
                            print(f"{artist} | {genre} | {song} | {length}")
    else:
        print("No solution found")


if __name__ == "__main__":
    main()