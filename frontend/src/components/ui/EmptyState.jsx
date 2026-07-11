import React from "react";
import { Card } from "@/components/ui/card";
import { FolderOpen } from "lucide-react";
import { motion } from "framer-motion";

export function EmptyState({ 
  icon: Icon = FolderOpen, 
  title = "No data available", 
  description = "There is currently no data to display here.", 
  action = null 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="flex flex-col items-center justify-center p-12 text-center border-white/5 bg-white/[0.01] min-h-[300px]">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/5 mb-6">
          <Icon className="h-8 w-8 text-white/40" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-white/50 max-w-sm mb-6">{description}</p>
        {action && <div>{action}</div>}
      </Card>
    </motion.div>
  );
}
