import { motion } from "framer-motion";
import { AlertTriangle, TrendingDown, Eye } from "lucide-react";

const reasons = [
  {
    icon: AlertTriangle,
    title: "AI Fails When Trust Breaks",
    description:
      "Even the most accurate AI becomes useless if operators consistently override its recommendations. Trust is the bridge between capability and adoption.",
    accent: "#6366F1",
  },
  {
    icon: TrendingDown,
    title: "Silent Overrides Kill Adoption",
    description:
      "When operators quietly bypass AI recommendations without logging reasons, organizations lose visibility into systemic trust issues until it's too late.",
    accent: "#7C3AED",
  },
  {
    icon: Eye,
    title: "Trust Must Be Measured",
    description:
      "You measure model accuracy, latency, and uptime. Trust should be treated as an equally critical metric with dashboards, alerts, and trend analysis.",
    accent: "#06B6D4",
  },
];

const ProductStory = () => {
  return (
    <section className="py-28 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4 text-white">
            Why Trust Analytics <span className="gradient-text">Matters</span>
          </h2>
          <p className="text-white/40 text-base max-w-xl mx-auto leading-relaxed">
            The missing observability layer in modern AI systems
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {reasons.map((reason, i) => (
            <motion.div
              key={reason.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="card-surface rounded-xl p-7 group cursor-default"
            >
              <div
                className="inline-flex items-center justify-center w-11 h-11 rounded-lg mb-5"
                style={{
                  background: `linear-gradient(135deg, ${reason.accent}20, ${reason.accent}08)`,
                }}
              >
                <reason.icon
                  className="w-5 h-5"
                  style={{ color: reason.accent }}
                />
              </div>
              <h3 className="text-[15px] font-semibold mb-2.5 text-white">
                {reason.title}
              </h3>
              <p className="text-sm text-white/40 leading-relaxed">
                {reason.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProductStory;
