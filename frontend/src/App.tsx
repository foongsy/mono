import { AgUiRuntimeProvider } from "./runtime/AgUiRuntimeProvider";
import { Thread } from "./components/assistant-ui/thread";

import "./App.css";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Agent Chat</h1>
      </header>
      <main className="app-main">
        <AgUiRuntimeProvider>
          <Thread />
        </AgUiRuntimeProvider>
      </main>
    </div>
  );
}
