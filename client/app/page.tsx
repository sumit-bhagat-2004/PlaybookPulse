import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Benefits from "@/components/Benefits";
import CTA from "@/components/CTA";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen bg-black">
      <Hero />
      <Features />
      <HowItWorks />
      <Benefits />
      <CTA />
    </div>
  );
}
