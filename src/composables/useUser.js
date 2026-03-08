// User role utilities
import { ref } from 'vue'

// Current user state
export const currentUser = ref(null)

// Role checking utilities
export function isAdmin(user) {
  return user?.role?.toLowerCase() === 'admin'
}

export function isManager(user) {
  return user?.role?.toLowerCase() === 'manager'
}

export function isUser(user) {
  return user?.role?.toLowerCase() === 'user'
}

export function hasRole(user, role) {
  if (!user?.role) return false
  return user.role.toLowerCase() === role.toLowerCase()
}

export function canManageUsers(user) {
  // Admin and manager can manage users
  return isAdmin(user) || isManager(user)
}

export function isAtLeastRole(user, requiredRole) {
  const roleHierarchy = { user: 1, manager: 2, admin: 3 }
  const userRole = user?.role?.toLowerCase() || ''
  const required = requiredRole.toLowerCase()
  
  return (roleHierarchy[userRole] || 0) >= (roleHierarchy[required] || 0)
}
