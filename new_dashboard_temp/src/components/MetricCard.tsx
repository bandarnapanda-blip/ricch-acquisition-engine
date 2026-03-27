import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../lib/utils';

interface MetricCardProps {
  label: string;
  value: string;
  sub?: string;
  change?: string;
  details?: {
    title: string;
    subtitle: string;
    stats: { label: string; value: string }[];
    rows: { label: string; value: string }[];
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  sub,
  change,
  details,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const isPositive = change?.startsWith('+');

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => details && setIsOpen(true)}
        className={cn(
          "liquid-glass rounded-3xl p-6 transition-all duration-300",
          details && "cursor-pointer hover:bg-white/50 dark:hover:bg-black/50"
        )}
      >
        <div className="text-xs font-medium text-apple-muted mb-2">
          {label}
        </div>
        <div className="text-4xl font-light tracking-tight text-apple-base">
          {value}
        </div>
        <div className="text-xs text-apple-muted mt-2">
          {sub}
        </div>
        {change && (
          <div className={cn(
            "text-xs font-medium mt-2 flex items-center gap-1",
            isPositive ? "text-success" : "text-danger"
          )}>
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {change}
          </div>
        )}
      </motion.div>

      <AnimatePresence>
        {isOpen && details && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="absolute inset-0 bg-black/20 dark:bg-black/40 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-2xl liquid-glass-panel rounded-[2rem] overflow-hidden"
            >
              <button
                onClick={() => setIsOpen(false)}
                className="absolute top-6 right-6 w-8 h-8 rounded-full liquid-glass-button flex items-center justify-center text-apple-muted transition-all"
              >
                <X size={16} />
              </button>

              <div className="p-10">
                <h3 className="text-2xl font-semibold tracking-tight text-apple-base mb-1">
                  {details.title}
                </h3>
                <p className="text-sm text-apple-muted mb-8">
                  {details.subtitle}
                </p>

                <div className="flex gap-px bg-white/20 dark:bg-black/20 rounded-2xl overflow-hidden mb-8 backdrop-blur-md">
                  {details.stats.map((stat, i) => (
                    <div key={i} className="flex-1 bg-white/30 dark:bg-black/30 p-6 text-center">
                      <div className="text-3xl font-light tracking-tight text-apple-base leading-none">
                        {stat.value}
                      </div>
                      <div className="text-xs font-medium text-apple-muted mt-2">
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="space-y-1">
                  {details.rows.map((row, i) => (
                    <div key={i} className="flex items-center justify-between py-3 border-b border-white/20 dark:border-white/10 last:border-0">
                      <span className="text-sm text-apple-muted">{row.label}</span>
                      <span className="text-sm text-apple-base font-medium">{row.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
