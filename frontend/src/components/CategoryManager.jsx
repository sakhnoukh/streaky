import { useState } from 'react'
import './CategoryManager.css'

const PRESET_COLORS = [
  '#6366f1', // Indigo
  '#8b5cf6', // Violet
  '#ec4899', // Pink
  '#ef4444', // Red
  '#f97316', // Orange
  '#eab308', // Yellow
  '#22c55e', // Green
  '#14b8a6', // Teal
  '#06b6d4', // Cyan
  '#3b82f6', // Blue
]

function CategoryManager({ categories, onAdd, onUpdate, onDelete, onClose }) {
  const [newName, setNewName] = useState('')
  const [newColor, setNewColor] = useState(PRESET_COLORS[0])
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')
  const [editColor, setEditColor] = useState('')

  const handleAdd = (e) => {
    e.preventDefault()
    if (newName.trim()) {
      onAdd(newName.trim(), newColor)
      setNewName('')
      setNewColor(PRESET_COLORS[0])
    }
  }

  const startEdit = (category) => {
    setEditingId(category.id)
    setEditName(category.name)
    setEditColor(category.color)
  }

  const handleUpdate = (categoryId) => {
    if (editName.trim()) {
      onUpdate(categoryId, editName.trim(), editColor)
      setEditingId(null)
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditName('')
    setEditColor('')
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="category-manager" onClick={(e) => e.stopPropagation()}>
        <div className="category-manager-header">
          <h2>📁 Manage Categories</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleAdd} className="category-form">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="New category name..."
            className="category-input"
            maxLength={50}
          />
          <div className="color-picker">
            {PRESET_COLORS.map((color) => (
              <button
                key={color}
                type="button"
                className={`color-option ${newColor === color ? 'selected' : ''}`}
                style={{ backgroundColor: color }}
                onClick={() => setNewColor(color)}
                title={color}
              />
            ))}
          </div>
          <button type="submit" className="add-category-btn" disabled={!newName.trim()}>
            + Add Category
          </button>
        </form>

        <div className="categories-list">
          {categories.length === 0 ? (
            <div className="no-categories">
              <p>No categories yet. Create one above!</p>
            </div>
          ) : (
            categories.map((category) => (
              <div key={category.id} className="category-item">
                {editingId === category.id ? (
                  <div className="category-edit-form">
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="category-edit-input"
                      maxLength={50}
                    />
                    <div className="color-picker small">
                      {PRESET_COLORS.map((color) => (
                        <button
                          key={color}
                          type="button"
                          className={`color-option small ${editColor === color ? 'selected' : ''}`}
                          style={{ backgroundColor: color }}
                          onClick={() => setEditColor(color)}
                        />
                      ))}
                    </div>
                    <div className="edit-actions">
                      <button onClick={() => handleUpdate(category.id)} className="save-btn">
                        Save
                      </button>
                      <button onClick={cancelEdit} className="cancel-btn">
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="category-info">
                      <span
                        className="category-color-badge"
                        style={{ backgroundColor: category.color }}
                      />
                      <span className="category-name">{category.name}</span>
                    </div>
                    <div className="category-actions">
                      <button
                        onClick={() => startEdit(category)}
                        className="edit-btn"
                        title="Edit category"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => onDelete(category.id)}
                        className="delete-btn"
                        title="Delete category"
                      >
                        🗑️
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default CategoryManager
