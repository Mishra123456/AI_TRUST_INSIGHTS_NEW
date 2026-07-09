import { motion } from "framer-motion";
import { Shield, Brain, Layers, Activity } from "lucide-react";

const capabilities = [
  {
    icon: Brain,
    title: "Predictive Trust Modeling",
    description:
      "Ensemble ML models identify patterns that predict when humans are likely to override AI decisions.",
    accent: "#6366F1",
  },
  {
    icon: Layers,
    title: "RAG-Based Explanations",
    description:
      "Retrieval-augmented generation clusters human feedback into interpretable trust themes.",
    accent: "#7C3AED",
  },
  {
    icon: Activity,
    title: "Behavioral Analytics",
    description:
      "Tracks override rates, sentiment shifts, and confidence decay over time.",
    accent: "#06B6D4",
  },
  {
    icon: Shield,
    title: "Responsible AI Monitoring",
    description:
      "Surfaces early warning signals for trust erosion, bias, and governance risks.",
    accent: "#10B981",
  },
];

const Capabilities = () => {
  return (
    <section className="py-28 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-white">
            Core <span className="gradient-text">Capabilities</span>
          </h2>
          <p className="text-white/40 text-base max-w-xl mx-auto leading-relaxed">
            Combining machine learning, NLP, and analytics to understand trust
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {capabilities.map((capability, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
              className="card-surface rounded-xl p-6 group cursor-default"
            >
              <div
                className="inline-flex items-center justify-center w-11 h-11 rounded-lg mb-4"
                style={{
                  background: `linear-gradient(135deg, ${capability.accent}20, ${capability.accent}08)`,
                }}
              >
                <capability.icon
                  className="w-5 h-5"
                  style={{ color: capability.accent }}
                />
              </div>

              <h3 className="text-[15px] font-semibold mb-2 text-white">
                {capability.title}
              </h3>

              <p className="text-sm text-white/40 leading-relaxed">
                {capability.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Capabilities;
