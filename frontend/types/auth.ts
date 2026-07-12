export type User = {
  id: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  role: "admin" | "user";
  created_at: string;
  updated_at: string;
};

export type Tokens = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
};
