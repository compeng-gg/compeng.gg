'use client';

//get number of test cases passed, 

interface ProgressTrackerProps {
  progress: number; 
  title: string;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ progress, title }) => {
  return (
    <div className="mx-auto my-2">
      <h2 className="text-lg font-semibold text-gray-900 mb-1">{title}</h2>
      <div className="relative pt-1">
        <div className="flex items-center justify-between text-xs font-medium text-gray-600">
          <span>0%</span>
          <span>100%</span>
        </div>
        <div className="relative pt-1">
          <div className="flex flex-col">
            <div className="flex-grow">
              <div
                className="bg-blue-600 h-2 rounded-lg"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
