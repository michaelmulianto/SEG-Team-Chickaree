def complete_round(my_round):
    for match in my_round.get_matches():
        match.result = 1
        match.save()
        match.black_player.round_eliminated = my_round.round_num
        match.black_player.save()