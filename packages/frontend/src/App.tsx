import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactFlowProvider } from "reactflow";
import FlowEditor from "@/editor/FlowEditor";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false, staleTime: 0, refetchOnWindowFocus: false },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactFlowProvider>
        <FlowEditor />
      </ReactFlowProvider>
    </QueryClientProvider>
  );
}
