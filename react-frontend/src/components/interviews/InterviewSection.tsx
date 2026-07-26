import { useEffect, useState } from "react";
import api from "../../utils/api";

import InterviewForm from "./InterviewForm";
import InterviewTable from "./InterviewTable";

import type {
  Candidate,
  Interview,
  InterviewFormData,
} from "./types";

const InterviewSection = () => {

  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  const [loading, setLoading] = useState(true);

  const [editingInterviewId, setEditingInterviewId] =
    useState<number | null>(null);

  const [formData, setFormData] =
    useState<InterviewFormData>({
      candidate_id: "",
      interviewer: "",
      interview_date: "",
      interview_time: "",
      interview_mode: "Online",
      meeting_link: "",
    });

  //---------------------------------------
  // Fetch Candidates
  //---------------------------------------

  const fetchCandidates = async () => {
    try {

      const response = await api.get("/candidates");

      setCandidates(response.data);

    } catch (error) {

      console.error("Failed to fetch candidates", error);

    }
  };

  //---------------------------------------
  // Fetch Interviews
  //---------------------------------------

  const fetchInterviews = async () => {

    try {

      const response = await api.get("/interviews");

      setInterviews(response.data);

    } catch (error) {

      console.error("Failed to fetch interviews", error);

    } finally {

      setLoading(false);

    }
  };

  //---------------------------------------
  // Initial Load
  //---------------------------------------

  useEffect(() => {

    fetchCandidates();

    fetchInterviews();

  }, []);

  //---------------------------------------
  // Schedule / Update Interview
  //---------------------------------------

  const handleSubmit = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    try {

      const payload = {

        candidate_id: Number(formData.candidate_id),

        interviewer: formData.interviewer,

        interview_date: formData.interview_date,

        interview_time: formData.interview_time,

        interview_mode: formData.interview_mode,

        meeting_link: formData.meeting_link,

      };

      //--------------------------------
      // Update
      //--------------------------------

      if (editingInterviewId !== null) {

        await api.put(
          `/interviews/${editingInterviewId}`,
          payload
        );

        alert("Interview updated successfully.");

      }

      //--------------------------------
      // Schedule
      //--------------------------------

      else {

        await api.post(
          "/interviews/schedule",
          payload
        );

        alert("Interview scheduled successfully.");

      }

      //--------------------------------
      // Reset Form
      //--------------------------------

      setFormData({

        candidate_id: "",

        interviewer: "",

        interview_date: "",

        interview_time: "",

        interview_mode: "Online",

        meeting_link: "",

      });

      setEditingInterviewId(null);

      fetchInterviews();

    }

    catch (error) {

      console.error(error);

      alert("Operation failed.");

    }

  };

  //---------------------------------------
  // Edit Interview
  //---------------------------------------

  const handleEdit = (
    interview: Interview
  ) => {

    setEditingInterviewId(interview.id);

    setFormData({

      candidate_id: interview.candidate_id,

      interviewer: interview.interviewer,

      interview_date: interview.interview_date,

      interview_time: interview.interview_time,

      interview_mode: interview.interview_mode,

      meeting_link: interview.meeting_link || "",

    });

    window.scrollTo({

      top: 0,

      behavior: "smooth",

    });

  };

  //---------------------------------------
  // Delete Interview
  //---------------------------------------

  const handleDelete = async (
    id: number
  ) => {

    const confirmDelete = window.confirm(
      "Delete this interview?"
    );

    if (!confirmDelete) return;

    try {

      await api.delete(`/interviews/${id}`);

      alert("Interview deleted.");

      fetchInterviews();

    }

    catch (error) {

      console.error(error);

      alert("Failed to delete interview.");

    }

  };

  //---------------------------------------
  // Candidate Name Helper
  //---------------------------------------

  const getCandidateName = (
    id: number
  ) => {

    const candidate = candidates.find(
      (c) => c.id === id
    );

    return candidate
      ? candidate.name
      : `Candidate #${id}`;
  };

  return (
        <div className="mt-10">

      {/* Header */}

      <div className="flex items-center justify-between mb-6">

        <div>

          <h2 className="text-3xl font-bold text-white">
            Interview Scheduling
          </h2>

          <p className="text-gray-400 mt-1">
            Schedule, update and manage candidate interviews.
          </p>

        </div>

        <div className="bg-blue-600 text-white px-5 py-3 rounded-xl">

          <div className="text-xs uppercase opacity-80">
            Total Interviews
          </div>

          <div className="text-2xl font-bold">
            {interviews.length}
          </div>

        </div>

      </div>

      {/* Form */}

      <InterviewForm

        formData={formData}

        setFormData={setFormData}

        candidates={candidates}

        onSubmit={handleSubmit}

        isEditing={editingInterviewId !== null}

      />

      {/* Loading */}

      {loading ? (

        <div className="bg-gray-900 rounded-xl p-10 text-center border border-gray-700">

          <div className="animate-pulse text-gray-400">

            Loading interviews...

          </div>

        </div>

      ) : (

        <>

          {/* Stats */}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">

            <div className="bg-gray-900 rounded-xl border border-gray-700 p-5">

              <p className="text-sm text-gray-400">
                Scheduled
              </p>

              <h3 className="text-3xl font-bold text-blue-400 mt-2">

                {
                  interviews.filter(
                    (i) =>
                      i.status.toLowerCase() ===
                      "scheduled"
                  ).length
                }

              </h3>

            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-700 p-5">

              <p className="text-sm text-gray-400">
                Completed
              </p>

              <h3 className="text-3xl font-bold text-green-400 mt-2">

                {
                  interviews.filter(
                    (i) =>
                      i.status.toLowerCase() ===
                      "completed"
                  ).length
                }

              </h3>

            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-700 p-5">

              <p className="text-sm text-gray-400">
                Cancelled
              </p>

              <h3 className="text-3xl font-bold text-red-400 mt-2">

                {
                  interviews.filter(
                    (i) =>
                      i.status.toLowerCase() ===
                      "cancelled"
                  ).length
                }

              </h3>

            </div>

            <div className="bg-gray-900 rounded-xl border border-gray-700 p-5">

              <p className="text-sm text-gray-400">
                Candidates
              </p>

              <h3 className="text-3xl font-bold text-yellow-400 mt-2">

                {candidates.length}

              </h3>

            </div>

          </div>

          {/* Empty State */}

          {interviews.length === 0 ? (

            <div className="bg-gray-900 rounded-xl border border-gray-700 p-10 text-center">

              <h3 className="text-xl font-semibold text-white mb-2">

                No Interviews Scheduled

              </h3>

              <p className="text-gray-400">

                Schedule your first interview using the form above.

              </p>

            </div>

          ) : (

            <InterviewTable

              interviews={interviews}

              onEdit={handleEdit}

              onDelete={handleDelete}

            />

          )}

          {/* Upcoming Interviews */}

          <div className="mt-8 bg-gray-900 border border-gray-700 rounded-xl p-6">

            <h3 className="text-xl font-bold text-white mb-5">

              Upcoming Interviews

            </h3>

            <div className="space-y-4">

              {interviews.slice(0, 5).map((interview) => (

                <div

                  key={interview.id}

                  className="flex justify-between items-center bg-gray-800 rounded-lg px-5 py-4"

                >

                  <div>

                    <h4 className="font-semibold text-white">

                      {getCandidateName(interview.candidate_id)}

                    </h4>

                    <p className="text-sm text-gray-400 mt-1">

                      {interview.interviewer}

                    </p>

                  </div>

                  <div className="text-right">

                    <p className="text-white">

                      {interview.interview_date}

                    </p>

                    <p className="text-gray-400 text-sm">

                      {interview.interview_time}

                    </p>

                  </div>

                </div>

              ))}

            </div>

          </div>

        </>

      )}

    </div>

  );

};

export default InterviewSection;