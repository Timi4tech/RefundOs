export type Role = "CUSTOMER" | "ADMIN" | "DEVELOPER";

export type RefundStatus =
  | "PENDING"
  | "PROCESSING"
  | "APPROVED"
  | "REJECTED"
  | "REQUIRES_REVIEW"
  | "COMPLETED"
  | "FAILED";

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Refund {
  id: string;
  user_id: string;
  transaction_id: string;
  amount: number | string;
  currency: string;
  reason: string;
  status: RefundStatus;
  created_at: string;
  updated_at: string;
  ai_category?: string | null;
  ai_risk_level?: "LOW" | "MEDIUM" | "HIGH" | null;
  ai_recommendation?: "APPROVE" | "REJECT" | "REVIEW" | null;
}

export interface AuditLog {
  id: string;
  refund_id?: string | null;
  actor_type: string;
  actor_id?: string | null;
  action: string;
  note: string;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
