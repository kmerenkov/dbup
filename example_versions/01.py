class Stage(object):
    def up(self, session):
        print "stage one, up!"
        session.execute("create table test (col1 integer);")

    def down(self, session):
        print "stage one, down!"
        session.execute("drop table test;")
