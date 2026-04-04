export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
export const WS_URL = BACKEND_URL.replace(/^http/, "ws") + "/ws";
