from sqlalchemy.orm import Session, selectinload

from app.models import Tag, Task


def list_tasks(db: Session) -> list[Task]:
    # 태그를 selectinload로 즉시 로딩합니다. 할 일 개수와 상관없이
    # 할 일 조회 1번 + 태그 조회 1번(IN 절)으로 끝나 N+1이 생기지 않습니다.
    return db.query(Task).options(selectinload(Task.tags)).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, title: str, tag_names: list[str]) -> Task:
    tags: list[Tag] = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)

    task = Task(title=title, tags=tags)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
