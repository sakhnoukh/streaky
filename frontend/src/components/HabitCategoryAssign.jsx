import { useState } from 'react'
import CategoryBadge from './CategoryBadge'
import './HabitCategoryAssign.css'

function HabitCategoryAssign({ habit, categories, onAddCategory, onRemoveCategory, onClose }) {
  const [selectedCategoryId, setSelectedCategoryId] = useState('')

  const habitCategoryIds = habit.categories?.map(c => c.id) || []
  const availableCategories = categories.filter(c => !habitCategoryIds.includes(c.id))

  const handleAdd = () => {
    if (selectedCategoryId) {
      onAddCategory(habit.id, parseInt(selectedCategoryId))
      setSelectedCategoryId('')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="habit-category-assign" onClick={(e) => e.stopPropagation()}>
        <div className="assign-header">
          <h2>🏷️ Categories for "{habit.name}"</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="current-categories">
          <h3>Current Categories</h3>
          {habit.categories && habit.categories.length > 0 ? (
            <div className="category-badges-list">
              {habit.categories.map((cat) => (
                <CategoryBadge
                  key={cat.id}
                  category={cat}
                  onRemove={() => onRemoveCategory(habit.id, cat.id)}
                />
              ))}
            </div>
          ) : (
            <p className="no-categories-text">No categories assigned yet</p>
          )}
        </div>

        {availableCategories.length > 0 && (
          <div className="add-category-section">
            <h3>Add Category</h3>
            <div className="add-category-form">
              <select
                value={selectedCategoryId}
                onChange={(e) => setSelectedCategoryId(e.target.value)}
                className="category-select"
              >
                <option value="">Select a category...</option>
                {availableCategories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
              <button
                onClick={handleAdd}
                disabled={!selectedCategoryId}
                className="add-btn"
              >
                + Add
              </button>
            </div>
          </div>
        )}

        {categories.length === 0 && (
          <p className="hint-text">
            No categories exist yet. Create some in the Category Manager first!
          </p>
        )}
      </div>
    </div>
  )
}

export default HabitCategoryAssign
