import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes";
import { ThemeProvider } from "@/context/ThemeContext";
import { AuthProvider } from "@/context/AuthContext";

import { GlobalToastListener } from "@/components/common/GlobalToastListener";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <GlobalToastListener>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </GlobalToastListener>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
