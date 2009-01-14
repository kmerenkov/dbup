class Stage(object):
    def up(self, session):
        session.execute("insert into test values (1);")

    def down(self, session):
        session.execute("delete from test where col1=1;")
