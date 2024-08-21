'use client';

import AdminPage from "./adminpage";

interface ProgressTrackerProps {
  testcasespassed: number; 
  totaltestcases: number;
  title: string;
  date: Date;
}


const ProgressTracker: React.FC<ProgressTrackerProps> = ({ testcasespassed, totaltestcases , title , date}) => {
    const progressPercentage = (testcasespassed / totaltestcases) * 100;
  return (
    <div className="mx-auto my-2">
      <h2 className="text-sm font-semibold text-gray-100 mb-1">{title}</h2>
      <div className="relative pt-1">
        <div className="flex items-center justify-between text-xs font-medium text-gray-600">
          <span>0%</span>
          <span>100%</span>
        </div>
        <div className="relative pt-1">
          <div className="flex flex-col">
            <div className="flex-grow bg-zinc-600 rounded-lg">
              <div
                className="bg-blue-600 h-2 rounded-lg"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
