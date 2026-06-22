import React, { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

import {
  FileText,
  Download,
  RefreshCw,
  Loader2,
  TrendingUp,
  CalendarCheck,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Sparkles
} from "lucide-react";

export const Reports = () => {
  const { refreshUser } = useAuth();

  // ======================================================
  // STATE MANAGEMENT
  // ======================================================

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // ======================================================
  // SAFE RESPONSE PARSER (IMPORTANT)
  // ======================================================

  const parseResponse = (res) => {
    if (!res) return [];
    if (Array.isArray(res)) return res;
    if (Array.isArray(res?.data)) return res.data;
    if (Array.isArray(res?.reports)) return res.reports;
    return [];
  };

  // ======================================================
  // FETCH REPORTS
  // ======================================================

  const fetchReports = useCallback(async () => {
    try {
      setError(null);

      const res = await api.get("/api/reports");

      const data = parseResponse(res);

      setReports(data);
    } catch (err) {
      console.error("Reports fetch error:", err);
      setError("Failed to load reports. Please try again.");
      setReports([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // ======================================================
  // GENERATE REPORT
  // ======================================================

  const handleGenerate = async () => {
    setGenerating(true);

    try {
      const res = await api.post("/api/reports/generate", {});

      const newReport =
        res?.data || res;

      if (newReport) {
        setReports((prev) => [newReport, ...prev]);
        setExpandedId(newReport?.id || null);
      }

      await refreshUser();
    } catch (err) {
      console.error("Generate report error:", err);
      setError("Failed to generate report.");
    } finally {
      setGenerating(false);
    }
  };

  // ======================================================
  // MANUAL REFRESH
  // ======================================================

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchReports();
  };

  // ======================================================
  // DOWNLOAD REPORT (SAFE)
  // ======================================================

  const handleDownload = async (reportId) => {
    try {
      const token = localStorage.getItem("greenmind_token");

      const res = await fetch(
        `http://127.0.0.1:8000/api/reports/${reportId}/download`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!res.ok) throw new Error("Download failed");

      const text = await res.text();

      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `greenmind_report_${reportId?.slice(0, 8) || "report"}.txt`;

      document.body.appendChild(a);
      a.click();
      a.remove();

      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download error:", err);
    }
  };

  // ======================================================
  // LOADING STATE
  // ======================================================

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 animate-spin text-green-600" />
      </div>
    );
  }

  // ======================================================
  // ERROR STATE
  // ======================================================

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mb-2" />
        <p className="text-red-500">{error}</p>

        <button
          onClick={fetchReports}
          className="mt-4 px-4 py-2 bg-green-600 text-white rounded-xl"
        >
          Retry
        </button>
      </div>
    );
  }

  // ======================================================
  // UI
  // ======================================================

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* HEADER */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-green-600" />
            AI Reports
          </h1>
          <p className="text-gray-500">
            Weekly sustainability insights powered by AI
          </p>
        </div>

        <div className="flex gap-2">

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-3 py-2 border rounded-xl"
          >
            {refreshing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
            {generating ? "Generating..." : "Generate"}
          </button>

        </div>
      </div>

      {/* EMPTY STATE */}
      {reports.length === 0 ? (
        <div className="text-center p-10 border rounded-xl">
          <FileText className="mx-auto w-10 h-10 text-gray-400" />
          <p className="mt-3 text-gray-500">
            No reports yet. Generate your first AI report.
          </p>
        </div>
      ) : (
        <div className="space-y-4">

          {reports.map((report, idx) => {
            const isOpen = expandedId === report?.id;

            return (
              <div
                key={report?.id || idx}
                className="border rounded-xl p-4 bg-white"
              >

                {/* HEADER */}
                <button
                  className="w-full flex justify-between items-center"
                  onClick={() =>
                    setExpandedId(isOpen ? null : report?.id)
                  }
                >
                  <div className="text-left">
                    <p className="font-semibold flex items-center gap-2">
                      <CalendarCheck className="w-4 h-4" />
                      Weekly Report
                    </p>

                    <p className="text-sm text-gray-500">
                      {report?.created_at
                        ? new Date(report.created_at).toDateString()
                        : "No date"}
                    </p>
                  </div>

                  {isOpen ? <ChevronUp /> : <ChevronDown />}
                </button>

                {/* BODY */}
                {isOpen && (
                  <div className="mt-4 space-y-4">

                    <p className="text-gray-700">
                      {report?.summary || "No summary available"}
                    </p>

                    <p className="text-blue-600 text-sm">
                      <TrendingUp className="inline w-4 h-4 mr-1" />
                      {report?.trends || "No trend data"}
                    </p>

                    <p className="font-bold text-green-600">
                      {report?.savings || "0 CO2 saved"}
                    </p>

                    {/* RECOMMENDATIONS SAFE */}
                    <div className="space-y-1">
                      {(report?.recommendations || []).map((rec, i) => (
                        <div key={i} className="text-sm">
                          {i + 1}. {rec}
                        </div>
                      ))}
                    </div>

                    {/* DOWNLOAD */}
                    <button
                      onClick={() => handleDownload(report?.id)}
                      className="text-blue-600 text-sm hover:underline"
                    >
                      <Download className="inline w-4 h-4 mr-1" />
                      Download Report
                    </button>

                  </div>
                )}

              </div>
            );
          })}

        </div>
      )}

    </div>
  );
};

export default Reports;