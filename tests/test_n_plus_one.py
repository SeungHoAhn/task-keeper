from sqlalchemy import event


def test_list_tasks_query_count_is_constant(client, db_session):
    for i in range(5):
        client.post("/tasks", json={"title": f"할 일 {i}", "tags": [f"태그{i}", "공통"]})

    # 이전 요청에서 로딩된 객체를 비워 실제 조회 쿼리를 셉니다.
    db_session.expire_all()

    statements: list[str] = []

    def count(conn, cursor, statement, *args):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", count)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", count)

    assert res.status_code == 200
    assert len(res.json()) == 5
    assert all(len(t["tags"]) == 2 for t in res.json())
    # 할 일 조회 1번 + 태그 조회 1번. N+1이면 1 + 5번이 됩니다.
    assert len(statements) == 2
