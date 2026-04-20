"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type RevenueChartProps = {
  monthlyPrice: number;
  yearOneRevenue: number;
  breakEvenMonth: number;
};

function buildRevenueSeries(
  monthlyPrice: number,
  yearOneRevenue: number,
  breakEvenMonth: number
) {
  const safeBreakEvenMonth = Math.min(Math.max(breakEvenMonth || 1, 1), 12);
  const monthlyTarget = Math.max(yearOneRevenue / 12, monthlyPrice);

  return Array.from({ length: 12 }, (_, index) => {
    const month = index + 1;
    const growthFactor = month / 12;
    const acceleration = month >= safeBreakEvenMonth ? 1.12 : 0.82;
    const revenue = Math.round(monthlyTarget * growthFactor * acceleration);

    return {
      month: `M${month}`,
      revenue
    };
  });
}

export function RevenueChart({
  monthlyPrice,
  yearOneRevenue,
  breakEvenMonth
}: RevenueChartProps) {
  const data = buildRevenueSeries(monthlyPrice, yearOneRevenue, breakEvenMonth);

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#61f0d1" stopOpacity={0.45} />
              <stop offset="95%" stopColor="#61f0d1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
          <XAxis dataKey="month" stroke="#94a3b8" tickLine={false} axisLine={false} />
          <YAxis
            stroke="#94a3b8"
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#09101d",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: "16px",
              color: "#e2e8f0"
            }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, "Revenue"]}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#61f0d1"
            strokeWidth={3}
            fill="url(#revenueGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
