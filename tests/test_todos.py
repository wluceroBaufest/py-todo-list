import pytest
from fastapi import status


class TestCreateTodo:
    """Tests for POST /todos/"""

    def test_create_todo_with_title_only(self, client):
        """Should create a todo with only title"""
        response = client.post(
            "/todos/",
            json={"title": "Test todo"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Test todo"
        assert data["description"] is None
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_todo_with_title_and_description(self, client):
        """Should create a todo with title and description"""
        response = client.post(
            "/todos/",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False

    def test_create_todo_without_title(self, client):
        """Should fail to create todo without title"""
        response = client.post(
            "/todos/",
            json={"description": "Missing title"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListTodos:
    """Tests for GET /todos/"""

    def test_list_empty_todos(self, client):
        """Should return empty list when no todos exist"""
        response = client.get("/todos/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_all_todos(self, client):
        """Should list all todos"""
        # Create some todos
        client.post("/todos/", json={"title": "Todo 1"})
        client.post("/todos/", json={"title": "Todo 2"})
        client.post("/todos/", json={"title": "Todo 3"})

        response = client.get("/todos/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Todo 1"
        assert data[1]["title"] == "Todo 2"
        assert data[2]["title"] == "Todo 3"

    def test_list_todos_filter_by_completed_true(self, client):
        """Should filter todos by completed=true"""
        # Create completed and uncompleted todos
        client.post("/todos/", json={"title": "Todo 1"})
        todo2 = client.post("/todos/", json={"title": "Todo 2"}).json()
        client.put(f"/todos/{todo2['id']}", json={"completed": True})
        client.post("/todos/", json={"title": "Todo 3"})

        response = client.get("/todos/?completed=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Todo 2"
        assert data[0]["completed"] is True

    def test_list_todos_filter_by_completed_false(self, client):
        """Should filter todos by completed=false"""
        # Create completed and uncompleted todos
        client.post("/todos/", json={"title": "Todo 1"})
        todo2 = client.post("/todos/", json={"title": "Todo 2"}).json()
        client.put(f"/todos/{todo2['id']}", json={"completed": True})
        client.post("/todos/", json={"title": "Todo 3"})

        response = client.get("/todos/?completed=false")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(not todo["completed"] for todo in data)


class TestGetTodo:
    """Tests for GET /todos/{id}"""

    def test_get_existing_todo(self, client):
        """Should retrieve an existing todo by id"""
        created = client.post(
            "/todos/",
            json={"title": "Test todo", "description": "Test description"}
        ).json()

        response = client.get(f"/todos/{created['id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created["id"]
        assert data["title"] == "Test todo"
        assert data["description"] == "Test description"

    def test_get_nonexistent_todo(self, client):
        """Should return 404 for non-existent todo"""
        response = client.get("/todos/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"


class TestUpdateTodo:
    """Tests for PUT /todos/{id}"""

    def test_update_todo_title(self, client):
        """Should update todo title"""
        created = client.post("/todos/", json={"title": "Original"}).json()

        response = client.put(
            f"/todos/{created['id']}",
            json={"title": "Updated"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated"
        assert data["description"] is None

    def test_update_todo_description(self, client):
        """Should update todo description"""
        created = client.post(
            "/todos/",
            json={"title": "Test", "description": "Original"}
        ).json()

        response = client.put(
            f"/todos/{created['id']}",
            json={"description": "Updated"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test"
        assert data["description"] == "Updated"

    def test_update_todo_completed_status(self, client):
        """Should update todo completed status"""
        created = client.post("/todos/", json={"title": "Test"}).json()
        assert created["completed"] is False

        response = client.put(
            f"/todos/{created['id']}",
            json={"completed": True}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is True

    def test_update_multiple_fields(self, client):
        """Should update multiple fields at once"""
        created = client.post(
            "/todos/",
            json={"title": "Original", "description": "Old desc"}
        ).json()

        response = client.put(
            f"/todos/{created['id']}",
            json={
                "title": "New title",
                "description": "New description",
                "completed": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New title"
        assert data["description"] == "New description"
        assert data["completed"] is True

    def test_update_nonexistent_todo(self, client):
        """Should return 404 when updating non-existent todo"""
        response = client.put(
            "/todos/999",
            json={"title": "Updated"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"

    def test_update_with_empty_body(self, client):
        """Should handle empty update (no changes)"""
        created = client.post("/todos/", json={"title": "Test"}).json()

        response = client.put(
            f"/todos/{created['id']}",
            json={}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test"


class TestDeleteTodo:
    """Tests for DELETE /todos/{id}"""

    def test_delete_existing_todo(self, client):
        """Should delete an existing todo"""
        created = client.post("/todos/", json={"title": "To be deleted"}).json()

        response = client.delete(f"/todos/{created['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's really deleted
        get_response = client.get(f"/todos/{created['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_todo(self, client):
        """Should return 404 when deleting non-existent todo"""
        response = client.delete("/todos/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"

    def test_delete_already_deleted_todo(self, client):
        """Should return 404 when trying to delete already deleted todo"""
        created = client.post("/todos/", json={"title": "Test"}).json()

        # Delete once
        client.delete(f"/todos/{created['id']}")

        # Try to delete again
        response = client.delete(f"/todos/{created['id']}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTodoWorkflow:
    """Integration tests for complete todo workflows"""

    def test_complete_todo_lifecycle(self, client):
        """Test creating, updating, retrieving and deleting a todo"""
        # Create
        create_response = client.post(
            "/todos/",
            json={"title": "Learn FastAPI", "description": "Build a REST API"}
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        todo = create_response.json()
        todo_id = todo["id"]

        # Retrieve
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["title"] == "Learn FastAPI"

        # Update
        update_response = client.put(
            f"/todos/{todo_id}",
            json={"completed": True}
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["completed"] is True

        # Delete
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        final_get = client.get(f"/todos/{todo_id}")
        assert final_get.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_todos_management(self, client):
        """Test managing multiple todos simultaneously"""
        # Create multiple todos
        todos = []
        for i in range(5):
            response = client.post(
                "/todos/",
                json={"title": f"Todo {i+1}"}
            )
            todos.append(response.json())

        # Mark some as completed
        for i in [0, 2, 4]:
            client.put(
                f"/todos/{todos[i]['id']}",
                json={"completed": True}
            )

        # Check completed filter
        completed = client.get("/todos/?completed=true").json()
        assert len(completed) == 3

        # Check uncompleted filter
        uncompleted = client.get("/todos/?completed=false").json()
        assert len(uncompleted) == 2

        # Check all todos
        all_todos = client.get("/todos/").json()
        assert len(all_todos) == 5
