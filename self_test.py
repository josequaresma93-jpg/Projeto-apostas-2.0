
from core.database import add_match

def seed_sample_data():
    sample = [
        ("2026-06-01","Série B","Vila Nova","Time A",2,1),
        ("2026-05-25","Série B","Vila Nova","Time B",1,0),
        ("2026-05-18","Série B","Vila Nova","Time C",1,1),
        ("2026-05-11","Série B","Vila Nova","Time D",0,0),
        ("2026-05-04","Série B","Vila Nova","Time E",2,0),
        ("2026-04-27","Série B","Vila Nova","Time K",3,1),
        ("2026-04-20","Série B","Vila Nova","Time L",0,1),
        ("2026-04-13","Série B","Vila Nova","Time M",1,1),
        ("2026-04-06","Série B","Vila Nova","Time N",2,2),
        ("2026-03-30","Série B","Vila Nova","Time O",1,0),
        ("2026-06-02","Série B","Time F","Novorizontino",1,1),
        ("2026-05-26","Série B","Time G","Novorizontino",0,2),
        ("2026-05-19","Série B","Time H","Novorizontino",2,1),
        ("2026-05-12","Série B","Time I","Novorizontino",1,0),
        ("2026-05-05","Série B","Time J","Novorizontino",1,1),
        ("2026-04-28","Série B","Time P","Novorizontino",0,0),
        ("2026-04-21","Série B","Time Q","Novorizontino",2,2),
        ("2026-04-14","Série B","Time R","Novorizontino",1,2),
        ("2026-04-07","Série B","Time S","Novorizontino",3,1),
        ("2026-03-31","Série B","Time T","Novorizontino",0,1),
    ]
    for x in sample:
        add_match(*x, source="sample")
