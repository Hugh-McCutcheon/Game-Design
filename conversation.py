on key press
    key == e:
        start conversation


player_choices = {
    1:'yes',
    2:'no'
}

enemy_responses = {
    'yes':'good',
    'no':'bad',
}


choice = selected_choice
playerresponce=player_choices[choice]
enemyresponce=enemy_responses[player_choices]