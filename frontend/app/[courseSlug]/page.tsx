import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/components/navbar';
import Table from '@/app/ui/table';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { TabMenu } from 'primereact/tabmenu';
import { Card } from 'primereact/card';
import StaffView from '../staffView/staff-view';

export interface Lab {
  name: string;
  slug: string;
  due_date: Date;
  grade: number;
  tasks: any;
}

function getRoleEnum(role) {
    const spIdx = role.lastIndexOf(' ');
    return role.substring(spIdx+1);
}

const leaderboardFields: [string, string][] = [
    ['id', 'ID'],
    ['speedup', 'Speedup'],
];

function Course({ params }: { params: { courseSlug: string } }) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [name, setName] = useState();
    const [labs, setLabs] = useState([] as Lab[]);
    const [role, setRole] = useState();

    // TODO: Enable navigation to this page only by instructor and TA role
    // Fetch and list all offerings for a given course in the same style and format as previous page for all courses
    useEffect(() => {
        async function fetchLabs() {
            try {
                //To do: include role in this API
                const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.courseSlug}/`, 'GET');
                const data = await response.json();
                setName(data.name);
                setLabs(data.assignments);
                setRole(getRoleEnum(data.role));
            } catch (error) {
                console.error('Error fetching labs:', error);
            }
        }

        fetchLabs();
    }, [params.courseSlug, jwt, setAndStoreJwt]);

  return (
    <WIP/>
  )
}

export default function Page({ params }: { params: { courseSlug: string } }) {
    return (
        <LoginRequired>
            <Course params={params} />
        </LoginRequired>
    );
}

function WIP(){
    return (
        <h4>This is a work in progress</h4>
    );
}
