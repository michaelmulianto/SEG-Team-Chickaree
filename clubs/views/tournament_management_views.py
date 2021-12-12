@login_required
@tournament_exists
def add_result_for_match(request, match_id):
    match = Match.objects.get(id=match_id)
    
