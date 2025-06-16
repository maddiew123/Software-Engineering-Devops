import dayjs from 'dayjs';
import MatchInput from '../components/MatchInput';
import HeaderComponent from '../components/HeaderComponent';
import { useUser } from '../useUser';

export default function createNewMatch() {
  const { user, loading } = useUser();

  const role = user?.role;
  const admin = role === "Manager";

  return (<>
    <HeaderComponent admin={admin} loggedIn={true} />
    {loading ? (
      <p>Loading...</p>
    ) :
      <MatchInput inlocation="" indate={dayjs('2025-04-17')} inopponent={0} inhome={0} admin={admin} />
    }</>)

}

