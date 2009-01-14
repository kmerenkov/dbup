class Stage(object):
    def up(self, session):
        session.execute("create table test (col1 integer);")

    def down(self, session):
        session.execute("drop table test;")
