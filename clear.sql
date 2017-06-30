delete from competitions where competition_id = '%s';
delete from entries where competition_id = '%s';
delete from events where competition_id = '%s';
delete from results where competition_id = '%s';
delete from placements where competition_id = '%s';
delete from judges where competition_id = '%s';
