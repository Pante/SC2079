import "@/styles/globals.css";
import Head from "next/head";
import Simulator from "components/Simulator";

export default function App() {
  return (
    <div>
      <Head>
        <title>MDP Algorithm Simulator</title>
      </Head>
      <Simulator />
    </div>
  );
}
