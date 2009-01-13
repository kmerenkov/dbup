class Stage(object):
    def up(self, session):
        print "stage two, up!"
        session.execute("insert into test values (1);")

    def down(self, session):
        print "stage two, down!"
        session.execute("delete from test where col1=1;")
