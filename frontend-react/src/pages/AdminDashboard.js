import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { 
  FiPlus, 
  FiEdit, 
  FiTrash2, 
  FiToggleLeft, 
  FiToggleRight,
  FiLogOut,
  FiShield,
  FiUsers,
  FiTarget,
  FiActivity,
  FiEye,
  FiSave,
  FiX,
  FiCheck
} from 'react-icons/fi';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [admin, setAdmin] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingRole, setViewingRole] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAdminAuth();
    fetchRoles();
  }, []);

  const checkAdminAuth = () => {
    const adminSession = localStorage.getItem('admin_session');
    if (!adminSession) {
      navigate('/admin');
      return;
    }
    setAdmin(JSON.parse(adminSession));
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get('http://localhost:8004/api/admin/roles');
      setRoles(response.data || []);
    } catch (error) {
      console.error('Failed to fetch roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_session');
    navigate('/admin');
  };

  const toggleRoleStatus = async (roleId) => {
    try {
      const response = await axios.patch(`http://localhost:8004/api/admin/roles/${roleId}/toggle`);
      if (response.data.success) {
        // Update local state
        setRoles(roles.map(role => 
          role.roleId === roleId 
            ? { ...role, isActive: response.data.isActive }
            : role
        ));
      }
    } catch (error) {
      console.error('Failed to toggle role status:', error);
      alert('Failed to update role status');
    }
  };

  const deleteRole = async (roleId, roleTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${roleTitle}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await axios.delete(`http://localhost:8004/api/admin/roles/${roleId}`);
      if (response.data.success) {
        setRoles(roles.filter(role => role.roleId !== roleId));
        alert(`Role "${roleTitle}" deleted successfully`);
      }
    } catch (error) {
      console.error('Failed to delete role:', error);
      alert('Failed to delete role: ' + (error.response?.data?.detail || error.message));
    }
  };

  const openAddModal = () => {
    setShowAddModal(true);
  };

  const openEditModal = (role) => {
    setEditingRole(role);
    setShowEditModal(true);
  };

  const openViewModal = (role) => {
    setViewingRole(role);
    setShowViewModal(true);
  };

  const handleRoleAdded = (newRole) => {
    setRoles([...roles, newRole]);
    setShowAddModal(false);
  };

  const handleRoleUpdated = (updatedRole) => {
    setRoles(roles.map(role => 
      role.roleId === updatedRole.roleId ? updatedRole : role
    ));
    setShowEditModal(false);
    setEditingRole(null);
  };

  const stats = {
    totalRoles: roles.length,
    activeRoles: roles.filter(role => role.isActive).length,
    inactiveRoles: roles.filter(role => !role.isActive).length
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="admin-header"
        >
          <div className="admin-title">
            <FiShield className="admin-icon" />
            <div>
              <h1>Admin Dashboard</h1>
              <p>Manage CareerBoost AI Roles</p>
            </div>
          </div>
          
          <div className="admin-user">
            <span>Welcome, {admin?.email}</span>
            <button onClick={handleLogout} className="logout-btn">
              <FiLogOut />
              Logout
            </button>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="admin-stats"
        >
          <div className="stat-card">
            <FiTarget className="stat-icon" />
            <div className="stat-content">
              <div className="stat-number">{stats.totalRoles}</div>
              <div className="stat-label">Total Roles</div>
            </div>
          </div>
          
          <div className="stat-card">
            <FiActivity className="stat-icon active" />
            <div className="stat-content">
              <div className="stat-number">{stats.activeRoles}</div>
              <div className="stat-label">Active Roles</div>
            </div>
          </div>
          
          <div className="stat-card">
            <FiUsers className="stat-icon inactive" />
            <div className="stat-content">
              <div className="stat-number">{stats.inactiveRoles}</div>
              <div className="stat-label">Inactive Roles</div>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="admin-actions"
        >
          <button className="add-role-btn" onClick={openAddModal}>
            <FiPlus />
            Add New Role
          </button>
        </motion.div>

        {/* Roles Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="roles-table-container"
        >
          <div className="table-header">
            <h2>Role Management</h2>
            <p>Manage all career roles displayed on the user dashboard</p>
          </div>
          
          <div className="roles-table">
            <div className="table-head">
              <div className="th">Order</div>
              <div className="th">Role Title</div>
              <div className="th">Subtitle</div>
              <div className="th">Status</div>
              <div className="th">Skills</div>
              <div className="th">Actions</div>
            </div>
            
            <div className="table-body">
              {roles.map((role, index) => (
                <motion.div
                  key={role.roleId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.4 + index * 0.05 }}
                  className={`table-row ${!role.isActive ? 'inactive' : ''}`}
                >
                  <div className="td order-cell">
                    <span className="order-badge">#{role.order}</span>
                  </div>
                  
                  <div className="td title-cell">
                    <div className="role-title">{role.title}</div>
                    <div className="role-id">ID: {role.roleId}</div>
                  </div>
                  
                  <div className="td subtitle-cell">
                    <div className="role-subtitle">{role.cardSubtitle}</div>
                  </div>
                  
                  <div className="td status-cell">
                    <button
                      onClick={() => toggleRoleStatus(role.roleId)}
                      className={`status-toggle ${role.isActive ? 'active' : 'inactive'}`}
                    >
                      {role.isActive ? <FiToggleRight /> : <FiToggleLeft />}
                      <span>{role.isActive ? 'Active' : 'Inactive'}</span>
                    </button>
                  </div>
                  
                  <div className="td skills-cell">
                    <div className="skills-count">
                      {role.mustHaveSkills?.length || 0} must-have
                    </div>
                    <div className="skills-count">
                      {role.goodToHaveSkills?.length || 0} good-to-have
                    </div>
                  </div>
                  
                  <div className="td actions-cell">
                    <button 
                      className="action-btn view"
                      onClick={() => openViewModal(role)}
                      title="View Role Details"
                    >
                      <FiEye />
                    </button>
                    <button 
                      className="action-btn edit"
                      onClick={() => openEditModal(role)}
                      title="Edit Role"
                    >
                      <FiEdit />
                    </button>
                    <button 
                      className="action-btn delete"
                      onClick={() => deleteRole(role.roleId, role.title)}
                      title="Delete Role"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
          
          {roles.length === 0 && (
            <div className="no-roles">
              <FiTarget className="no-roles-icon" />
              <p>No roles found</p>
              <p>Add your first role to get started</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Add Role Modal */}
      <AnimatePresence>
        {showAddModal && (
          <AddRoleModal 
            onClose={() => setShowAddModal(false)}
            onRoleAdded={handleRoleAdded}
          />
        )}
      </AnimatePresence>

      {/* Edit Role Modal */}
      <AnimatePresence>
        {showEditModal && editingRole && (
          <EditRoleModal 
            role={editingRole}
            onClose={() => {
              setShowEditModal(false);
              setEditingRole(null);
            }}
            onRoleUpdated={handleRoleUpdated}
          />
        )}
      </AnimatePresence>

      {/* View Role Modal */}
      <AnimatePresence>
        {showViewModal && viewingRole && (
          <ViewRoleModal 
            role={viewingRole}
            onClose={() => {
              setShowViewModal(false);
              setViewingRole(null);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Add Role Modal Component
const AddRoleModal = ({ onClose, onRoleAdded }) => {
  const [formData, setFormData] = useState({
    roleId: '',
    title: '',
    cardSubtitle: '',
    order: '',
    overview: '',
    responsibilities: [''],
    mustHaveSkills: [''],
    goodToHaveSkills: [''],
    tools: [''],
    extraQuestions: [''],
    interviewTopics: [''],
    projectIdeas: [''],
    learningResources: [''],
    faqs: [''],
    salaryRange: { min: '', max: '', currency: 'USD' },
    experienceLevel: '',
    remoteWork: false,
    industryDemand: 'Medium'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Clean up arrays (remove empty strings)
      const cleanData = {
        ...formData,
        order: parseInt(formData.order),
        responsibilities: formData.responsibilities.filter(item => item.trim()),
        mustHaveSkills: formData.mustHaveSkills.filter(item => item.trim()),
        goodToHaveSkills: formData.goodToHaveSkills.filter(item => item.trim()),
        tools: formData.tools.filter(item => item.trim()),
        extraQuestions: formData.extraQuestions.filter(item => item.trim()),
        interviewTopics: formData.interviewTopics.filter(item => item.trim()),
        projectIdeas: formData.projectIdeas.filter(item => item.trim()),
        learningResources: formData.learningResources.filter(item => item.trim()),
        faqs: formData.faqs.filter(item => item.trim()),
        salaryRange: {
          min: formData.salaryRange.min ? parseInt(formData.salaryRange.min) : 0,
          max: formData.salaryRange.max ? parseInt(formData.salaryRange.max) : 0,
          currency: formData.salaryRange.currency || 'USD'
        },
        isActive: true
      };

      const response = await axios.post('http://localhost:8004/api/admin/roles', cleanData);
      if (response.data) {
        onRoleAdded(response.data);
        alert('Role added successfully!');
      }
    } catch (error) {
      console.error('Failed to add role:', error);
      alert('Failed to add role: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({ ...formData, [field]: newArray });
  };

  const addArrayItem = (field) => {
    setFormData({ ...formData, [field]: [...formData[field], ''] });
  };

  const removeArrayItem = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData({ ...formData, [field]: newArray });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="modal-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="role-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>Add New Role</h2>
          <button onClick={onClose} className="modal-close">
            <FiX />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="role-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Role ID *</label>
              <input
                type="text"
                value={formData.roleId}
                onChange={(e) => setFormData({ ...formData, roleId: e.target.value })}
                placeholder="e.g., ai-engineer"
                required
              />
            </div>

            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., AI Engineer"
                required
              />
            </div>

            <div className="form-group">
              <label>Card Subtitle *</label>
              <input
                type="text"
                value={formData.cardSubtitle}
                onChange={(e) => setFormData({ ...formData, cardSubtitle: e.target.value })}
                placeholder="Short description for dashboard card"
                required
              />
            </div>

            <div className="form-group">
              <label>Display Order *</label>
              <input
                type="number"
                value={formData.order}
                onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                placeholder="e.g., 11"
                required
                min="1"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Overview *</label>
            <textarea
              value={formData.overview}
              onChange={(e) => setFormData({ ...formData, overview: e.target.value })}
              placeholder="Detailed role description..."
              rows="4"
              required
            />
          </div>

          {/* Array Fields */}
          {['responsibilities', 'mustHaveSkills', 'goodToHaveSkills', 'tools', 'extraQuestions', 'interviewTopics', 'projectIdeas', 'learningResources', 'faqs'].map(field => (
            <div key={field} className="form-group array-field">
              <label>
                {field === 'responsibilities' && 'Responsibilities'}
                {field === 'mustHaveSkills' && 'Must-Have Skills'}
                {field === 'goodToHaveSkills' && 'Good-to-Have Skills'}
                {field === 'tools' && 'Tools & Technologies'}
                {field === 'extraQuestions' && 'Extra Questions'}
                {field === 'interviewTopics' && 'Interview Topics'}
                {field === 'projectIdeas' && 'Project Ideas'}
                {field === 'learningResources' && 'Learning Resources'}
                {field === 'faqs' && 'Frequently Asked Questions'}
              </label>
              {formData[field].map((item, index) => (
                <div key={index} className="array-item">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => handleArrayChange(field, index, e.target.value)}
                    placeholder={`Enter ${field.slice(0, -1)}...`}
                  />
                  <button
                    type="button"
                    onClick={() => removeArrayItem(field, index)}
                    className="remove-btn"
                  >
                    <FiX />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => addArrayItem(field)}
                className="add-item-btn"
              >
                <FiPlus /> Add Item
              </button>
            </div>
          ))}

          {/* Additional Fields */}
          <div className="form-section">
            <h3>Additional Information</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Experience Level</label>
                <select
                  value={formData.experienceLevel}
                  onChange={(e) => setFormData({ ...formData, experienceLevel: e.target.value })}
                >
                  <option value="">Select Level</option>
                  <option value="Entry Level">Entry Level</option>
                  <option value="Mid Level">Mid Level</option>
                  <option value="Senior Level">Senior Level</option>
                  <option value="Expert Level">Expert Level</option>
                </select>
              </div>

              <div className="form-group">
                <label>Industry Demand</label>
                <select
                  value={formData.industryDemand}
                  onChange={(e) => setFormData({ ...formData, industryDemand: e.target.value })}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Very High">Very High</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.remoteWork}
                  onChange={(e) => setFormData({ ...formData, remoteWork: e.target.checked })}
                />
                Remote Work Available
              </label>
            </div>

            <div className="form-group">
              <label>Salary Range (USD)</label>
              <div className="salary-range">
                <input
                  type="number"
                  placeholder="Min"
                  value={formData.salaryRange.min}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    salaryRange: { ...formData.salaryRange, min: e.target.value }
                  })}
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={formData.salaryRange.max}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    salaryRange: { ...formData.salaryRange, max: e.target.value }
                  })}
                />
              </div>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Adding...' : 'Add Role'}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

// Edit Role Modal Component
const EditRoleModal = ({ role, onClose, onRoleUpdated }) => {
  const [formData, setFormData] = useState({
    title: role.title || '',
    cardSubtitle: role.cardSubtitle || '',
    order: role.order || '',
    overview: role.overview || '',
    responsibilities: role.responsibilities || [''],
    mustHaveSkills: role.mustHaveSkills || [''],
    goodToHaveSkills: role.goodToHaveSkills || [''],
    tools: role.tools || [''],
    extraQuestions: role.extraQuestions || [''],
    interviewTopics: role.interviewTopics || [''],
    projectIdeas: role.projectIdeas || [''],
    learningResources: role.learningResources || [''],
    faqs: role.faqs || [''],
    salaryRange: role.salaryRange || { min: '', max: '', currency: 'USD' },
    experienceLevel: role.experienceLevel || '',
    remoteWork: role.remoteWork || false,
    industryDemand: role.industryDemand || 'Medium'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const cleanData = {
        ...formData,
        order: parseInt(formData.order),
        responsibilities: formData.responsibilities.filter(item => item.trim()),
        mustHaveSkills: formData.mustHaveSkills.filter(item => item.trim()),
        goodToHaveSkills: formData.goodToHaveSkills.filter(item => item.trim()),
        tools: formData.tools.filter(item => item.trim()),
        extraQuestions: formData.extraQuestions.filter(item => item.trim()),
        interviewTopics: formData.interviewTopics.filter(item => item.trim()),
        projectIdeas: formData.projectIdeas.filter(item => item.trim()),
        learningResources: formData.learningResources.filter(item => item.trim()),
        faqs: formData.faqs.filter(item => item.trim()),
        salaryRange: {
          min: formData.salaryRange.min ? parseInt(formData.salaryRange.min) : 0,
          max: formData.salaryRange.max ? parseInt(formData.salaryRange.max) : 0,
          currency: formData.salaryRange.currency || 'USD'
        }
      };

      const response = await axios.put(`http://localhost:8004/api/admin/roles/${role.roleId}`, cleanData);
      if (response.data) {
        onRoleUpdated(response.data);
        alert('Role updated successfully!');
      }
    } catch (error) {
      console.error('Failed to update role:', error);
      alert('Failed to update role: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleArrayChange = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({ ...formData, [field]: newArray });
  };

  const addArrayItem = (field) => {
    setFormData({ ...formData, [field]: [...formData[field], ''] });
  };

  const removeArrayItem = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData({ ...formData, [field]: newArray });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="modal-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="role-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>Edit Role: {role.title}</h2>
          <button onClick={onClose} className="modal-close">
            <FiX />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="role-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Role ID</label>
              <input
                type="text"
                value={role.roleId}
                disabled
                className="disabled-input"
              />
              <small>Role ID cannot be changed</small>
            </div>

            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Card Subtitle *</label>
              <input
                type="text"
                value={formData.cardSubtitle}
                onChange={(e) => setFormData({ ...formData, cardSubtitle: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Display Order *</label>
              <input
                type="number"
                value={formData.order}
                onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                required
                min="1"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Overview *</label>
            <textarea
              value={formData.overview}
              onChange={(e) => setFormData({ ...formData, overview: e.target.value })}
              rows="4"
              required
            />
          </div>

          {/* Array Fields */}
          {['responsibilities', 'mustHaveSkills', 'goodToHaveSkills', 'tools', 'extraQuestions', 'interviewTopics', 'projectIdeas', 'learningResources', 'faqs'].map(field => (
            <div key={field} className="form-group array-field">
              <label>
                {field === 'responsibilities' && 'Responsibilities'}
                {field === 'mustHaveSkills' && 'Must-Have Skills'}
                {field === 'goodToHaveSkills' && 'Good-to-Have Skills'}
                {field === 'tools' && 'Tools & Technologies'}
                {field === 'extraQuestions' && 'Extra Questions'}
                {field === 'interviewTopics' && 'Interview Topics'}
                {field === 'projectIdeas' && 'Project Ideas'}
                {field === 'learningResources' && 'Learning Resources'}
                {field === 'faqs' && 'Frequently Asked Questions'}
              </label>
              {formData[field].map((item, index) => (
                <div key={index} className="array-item">
                  <input
                    type="text"
                    value={item}
                    onChange={(e) => handleArrayChange(field, index, e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => removeArrayItem(field, index)}
                    className="remove-btn"
                  >
                    <FiX />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => addArrayItem(field)}
                className="add-item-btn"
              >
                <FiPlus /> Add Item
              </button>
            </div>
          ))}

          {/* Additional Fields */}
          <div className="form-section">
            <h3>Additional Information</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Experience Level</label>
                <select
                  value={formData.experienceLevel}
                  onChange={(e) => setFormData({ ...formData, experienceLevel: e.target.value })}
                >
                  <option value="">Select Level</option>
                  <option value="Entry Level">Entry Level</option>
                  <option value="Mid Level">Mid Level</option>
                  <option value="Senior Level">Senior Level</option>
                  <option value="Expert Level">Expert Level</option>
                </select>
              </div>

              <div className="form-group">
                <label>Industry Demand</label>
                <select
                  value={formData.industryDemand}
                  onChange={(e) => setFormData({ ...formData, industryDemand: e.target.value })}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Very High">Very High</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.remoteWork}
                  onChange={(e) => setFormData({ ...formData, remoteWork: e.target.checked })}
                />
                Remote Work Available
              </label>
            </div>

            <div className="form-group">
              <label>Salary Range (USD)</label>
              <div className="salary-range">
                <input
                  type="number"
                  placeholder="Min"
                  value={formData.salaryRange.min}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    salaryRange: { ...formData.salaryRange, min: e.target.value }
                  })}
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={formData.salaryRange.max}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    salaryRange: { ...formData.salaryRange, max: e.target.value }
                  })}
                />
              </div>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Updating...' : 'Update Role'}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

// View Role Modal Component
const ViewRoleModal = ({ role, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="modal-overlay"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="role-modal view-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>{role.title}</h2>
          <button onClick={onClose} className="modal-close">
            <FiX />
          </button>
        </div>

        <div className="role-view-content">
          <div className="view-section">
            <h3>Basic Information</h3>
            <div className="info-grid">
              <div><strong>Role ID:</strong> {role.roleId}</div>
              <div><strong>Order:</strong> #{role.order}</div>
              <div><strong>Status:</strong> {role.isActive ? '🟢 Active' : '🔴 Inactive'}</div>
              <div><strong>Subtitle:</strong> {role.cardSubtitle}</div>
              <div><strong>Experience Level:</strong> {role.experienceLevel || 'Not specified'}</div>
              <div><strong>Industry Demand:</strong> {role.industryDemand || 'Medium'}</div>
              <div><strong>Remote Work:</strong> {role.remoteWork ? '✅ Available' : '❌ Not Available'}</div>
              <div><strong>Salary Range:</strong> {
                role.salaryRange?.min && role.salaryRange?.max 
                  ? `$${role.salaryRange.min.toLocaleString()} - $${role.salaryRange.max.toLocaleString()}`
                  : 'Not specified'
              }</div>
            </div>
          </div>

          <div className="view-section">
            <h3>Overview</h3>
            <p>{role.overview}</p>
          </div>

          <div className="view-section">
            <h3>Responsibilities ({role.responsibilities?.length || 0})</h3>
            <ul>
              {role.responsibilities?.map((resp, index) => (
                <li key={index}>{resp}</li>
              ))}
            </ul>
          </div>

          <div className="view-section">
            <h3>Must-Have Skills ({role.mustHaveSkills?.length || 0})</h3>
            <div className="skills-tags">
              {role.mustHaveSkills?.map((skill, index) => (
                <span key={index} className="skill-tag must-have">{skill}</span>
              ))}
            </div>
          </div>

          <div className="view-section">
            <h3>Good-to-Have Skills ({role.goodToHaveSkills?.length || 0})</h3>
            <div className="skills-tags">
              {role.goodToHaveSkills?.map((skill, index) => (
                <span key={index} className="skill-tag good-to-have">{skill}</span>
              ))}
            </div>
          </div>

          <div className="view-section">
            <h3>Tools & Technologies ({role.tools?.length || 0})</h3>
            <div className="skills-tags">
              {role.tools?.map((tool, index) => (
                <span key={index} className="skill-tag tool">{tool}</span>
              ))}
            </div>
          </div>

          {role.extraQuestions?.length > 0 && (
            <div className="view-section">
              <h3>Extra Questions ({role.extraQuestions.length})</h3>
              <ul>
                {role.extraQuestions.map((question, index) => (
                  <li key={index}>{question}</li>
                ))}
              </ul>
            </div>
          )}

          {role.interviewTopics?.length > 0 && (
            <div className="view-section">
              <h3>Interview Topics ({role.interviewTopics.length})</h3>
              <div className="skills-tags">
                {role.interviewTopics.map((topic, index) => (
                  <span key={index} className="skill-tag interview">{topic}</span>
                ))}
              </div>
            </div>
          )}

          {role.projectIdeas?.length > 0 && (
            <div className="view-section">
              <h3>Project Ideas ({role.projectIdeas.length})</h3>
              <ul>
                {role.projectIdeas.map((project, index) => (
                  <li key={index}>{project}</li>
                ))}
              </ul>
            </div>
          )}

          {role.learningResources?.length > 0 && (
            <div className="view-section">
              <h3>Learning Resources ({role.learningResources.length})</h3>
              <ul>
                {role.learningResources.map((resource, index) => (
                  <li key={index}>{resource}</li>
                ))}
              </ul>
            </div>
          )}

          {role.faqs?.length > 0 && (
            <div className="view-section">
              <h3>FAQs ({role.faqs.length})</h3>
              <ul>
                {role.faqs.map((faq, index) => (
                  <li key={index}>{faq}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="view-section">
            <h3>Timestamps</h3>
            <div className="info-grid">
              <div><strong>Created:</strong> {new Date(role.createdAt).toLocaleString()}</div>
              <div><strong>Updated:</strong> {new Date(role.updatedAt).toLocaleString()}</div>
            </div>
          </div>
        </div>

        <div className="modal-actions">
          <button onClick={onClose} className="btn btn-primary">
            Close
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AdminDashboard;