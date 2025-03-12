import React, { ReactNode, useContext, useEffect, useState } from 'react';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchUserName } from '@/app/lib/getUser';
import { InputText } from 'primereact/inputtext';
import { Checkbox } from 'primereact/checkbox';
import { Calendar } from 'primereact/calendar';
import { Divider } from 'primereact/divider';

export interface StaffCourseSettingsTabProps {
    courseSlug: string;
    offeringSlug: string;
}

interface OfferingTeamsSettings {
    max_team_size: number | null;
    formation_deadline: string | null;
}

export default function StaffCourseSettingsTab(props: StaffCourseSettingsTabProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const {courseSlug, offeringSlug} = props;
    const [offeringTeamsSettings, setOfferingTeamsSettings] = useState<OfferingTeamsSettings>({
        max_team_size: null,
        formation_deadline: null
    });
    const [formData, setFormData] = useState<OfferingTeamsSettings>({
        max_team_size: null,
        formation_deadline: null
    });
    const [loading, setLoading] = useState<boolean>(true);
    const [userName, setUserName] = useState<string>('');
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Fetch username on component mount
    useEffect(() => {
        fetchUserName(jwt, setAndStoreJwt)
            .then((fetchedUserName) => {
                setUserName(fetchedUserName); // Set the username in state
            }).catch((error) => console.error('Failed to fetch username:', error));
    }, [jwt, setAndStoreJwt]);

    // Fetch teams whenever userName is set
    useEffect(() => {
        if (userName) {
            fetchOfferingTeamsSettings();
        }
    }, [userName]);

    // Fetch teams function, accessible to all parts of the file
    const fetchOfferingTeamsSettings = async () => {
        try {
            setLoading(true);
            const res = await fetchApi(jwt, setAndStoreJwt, `teams/settings/get/${courseSlug}/${offeringSlug}`, 'GET');
            const teamsSettings = await res.json();
            console.log(teamsSettings);
            setOfferingTeamsSettings(teamsSettings);
            setFormData(teamsSettings);
        } catch (error) {
            console.error('Failed to retrieve teams', error);
        } finally {
            setLoading(false);
        }
    };

    const createOfferingTeamsSettings = async () => {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `teams/settings/create/${courseSlug}/${offeringSlug}`, 'POST');
            const createdSettings = await res.json();
            setOfferingTeamsSettings(createdSettings);
            setFormData(createdSettings);
        } catch (error) {
            console.error('Failed to create team settings:', error);
        }
    };

    const updateOfferingTeamsSettings = async () => {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `teams/settings/update/${courseSlug}/${offeringSlug}`, 'PATCH', {
                max_team_size: formData.max_team_size,
                formation_deadline: formData.formation_deadline
            });
            if (res.ok) {
                setSuccessMessage('Update successful!'); // Set success message
                setTimeout(() => setSuccessMessage(null), 3000); // Clear message after 3 seconds
                const updatedSettings = await res.json();
                setOfferingTeamsSettings(updatedSettings);
                setFormData(updatedSettings);
            } else {
                console.error('Failed to update settings');
                setSuccessMessage('Update failed!'); // Set failure message
                setTimeout(() => setSuccessMessage(null), 3000); // Clear message after 3 seconds
            }
        } catch (error) {
            console.error('Failed to update team settings', error);
        }
    }; 

    // Handle form input changes
    const handleInputChange = (field: string, value: any) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    if (loading) return <p>Loading...</p>;

    return (
        <div>
            {offeringTeamsSettings.max_team_size ? (
                <div>
                    <WIP/>
                    <Divider/>
                    <h3>Edit Team Settings</h3>
                    <div style={{ marginBottom: '1em' }}>
                        <label htmlFor="max_team_size">Max Team Size </label>
                        <InputText
                            id="max_team_size"
                            value={formData.max_team_size?.toString() || ''}
                            onChange={(e) => {
                                const value = e.target.value;
                                const numericValue = value ? parseInt(value) : null;
                                if (numericValue != null && !isNaN(numericValue) || value === '') {
                                    handleInputChange('max_team_size', numericValue);
                                }
                            }}
                        />
                    </div>
                    <div style={{ marginBottom: '1em' }}>
                        <label htmlFor="formation_deadline">Formation Deadline </label>
                        <Calendar
                            id="formation_deadline"
                            value={formData.formation_deadline ? new Date(formData.formation_deadline) : null}
                            onChange={(e) => {
                                if (e.value) {
                                    handleInputChange('formation_deadline', e.value);
                                } else {
                                    handleInputChange('formation_deadline', null); // Handle null case
                                }   
                            }}
                            showTime
                        />
                    </div>
                    <Divider/>
                    <Button label="Save Settings" onClick={updateOfferingTeamsSettings} />
                    {successMessage && (
                        <div style={{ marginTop: '1em', color: 'green' }}>
                            <strong>{successMessage}</strong>
                        </div>
                    )}
                </div>
            ) : (
                <div>
                    <h3>Teams are not initialized</h3>
                    <Button label="Create Team Settings" onClick={createOfferingTeamsSettings} />
                </div>
            )}
        </div>
    );
}

function WIP(){
    return (
        <h4>This is a work in progress</h4>
    );
}
