// Type declarations for JavaScript modules

declare module '@/utils/api' {
  export function getApiUrl(): string
}

declare module '@/composables/useUser' {
  import { Ref } from 'vue'
  
  export interface User {
    id: string
    email: string
    name?: string
    role: string
    timezone?: string
    is_active: boolean
  }
  
  export const currentUser: Ref<User | null>
  
  export function isAdmin(user: User | null): boolean
  export function isManager(user: User | null): boolean
  export function isUser(user: User | null): boolean
  export function hasRole(user: User | null, role: string): boolean
  export function canManageUsers(user: User | null): boolean
  export function isAtLeastRole(user: User | null, requiredRole: string): boolean
}

declare module '@/composables/useToast' {
  import { Ref } from 'vue'
  
  export interface Toast {
    id: number
    message: string
    variant: string
  }
  
  export function useToast(): {
    show: Ref<boolean>
    create: (options: {
      title?: string
      message?: string
      variant?: string
      modelValue?: number
    }) => void
    success: (message: string, title?: string) => void
    danger: (message: string, title?: string) => void
    warning: (message: string, title?: string) => void
    info: (message: string, title?: string) => void
  }
}
