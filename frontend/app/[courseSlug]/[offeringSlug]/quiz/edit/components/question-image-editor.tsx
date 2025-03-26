
import React, { useContext, useEffect, useRef, useState } from 'react';
import { Toast } from 'primereact/toast';
import { FileUpload, FileUploadHandlerEvent, FileUploadHeaderTemplateOptions, FileUploadSelectEvent, FileUploadUploadEvent, ItemTemplateOptions,} from 'primereact/fileupload';
import { ProgressBar } from 'primereact/progressbar';
import { Button } from 'primereact/button';
import { Tooltip } from 'primereact/tooltip';
import { Tag } from 'primereact/tag';
import { ID_SET_ON_SERVER, QuestionImage } from '../../question-models';
import { fetchImages, fetchImagesAsFiles } from '../../quiz-utilities';
import { JwtContext } from '@/app/lib/jwt-provider';
import { FileUpload as FileUploadRefType } from "primereact/fileupload";
import { Image } from "primereact/image";
import { de, id } from 'date-fns/locale';
import { TextInput } from 'primereact/textinput';
import { InputText } from 'primereact/inputtext';
import { ButtonGroup } from 'primereact/buttongroup';


export interface QuestionImageUploaderProps {
    images: QuestionImage[];
    setImages: (images: QuestionImage[]) => void;
    courseSlug: string;
    quizSlug: string;
}

export default function QuestionImageUploader(props: QuestionImageUploaderProps) {
    const fileUploadRef = useRef<FileUploadRefType | null>(null);
    const [allFiles, setAllFiles] = useState<(File | undefined)[]>([]);
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const { images, courseSlug, quizSlug, setImages } = props;

    const [loaded, setLoaded]   = useState<boolean>(false);

    //Load files from server that already exist -> do this on reload
    useEffect(() => {
        const setFiles = async () => {
            setAllFiles(await fetchImagesAsFiles(images, courseSlug, quizSlug, jwt, setAndStoreJwt) ?? []);
            setLoaded(true);
        }
        if(!loaded) setFiles()
    }, [loaded, images]);
    

    const handleNewImages = (event: FileUploadHandlerEvent) => {
        const newFiles = event.files as File[];
        setAllFiles((prev) => [...prev, ...newFiles]);
        setImages([...images, ...newFiles.map((f) => ({ id: ID_SET_ON_SERVER, caption: '', status: 'NEW', file: f } as QuestionImage))]);
        fileUploadRef.current?.clear();
    };

    const setCaption = (index: number, caption: string) => {
        const newImages = [...images];
        newImages[index].caption = caption;
        if(newImages[index].status == 'UNMODIFIED') newImages[index].status = 'MODIFIED';
        setImages(newImages);
        console.log(JSON.stringify(images, null, 2));
    }

    const moveImage = (index: number, offset: number) => {
        const newImages = [...images];
        const temp = newImages[index];
        newImages[index] = newImages[index + offset];
        //modify moved images
        if(newImages[index].status == 'UNMODIFIED') newImages[index].status = 'MODIFIED';
        if(newImages[index + offset].status == 'UNMODIFIED') newImages[index + offset].status = 'MODIFIED';
        newImages[index + offset] = temp;
        setImages(newImages);
        const newRender = [...allFiles];
        newRender[index] = allFiles[index + offset];
        newRender[index + offset] = allFiles[index];
        setAllFiles(allFiles);
    }

    const deleteImage = (index: number) => {
        const newImages = [...images];
        const newRender = [...allFiles];
        if(images[index].status != 'NEW'){
            newImages[index].status = 'DELETED';
            newRender[index] = undefined;
        } else { //can just remove deleted images
            newImages.splice(index, 1);
            newRender.splice(index, 1);
        }
        setImages(newImages);
        setAllFiles(newRender);
    }




    return (
        <div className="p-4 space-y-4">
            <div className="flex flex-wrap gap-3">
                {allFiles.map((file, idx) => {
                    if(file == undefined || idx >= images.length || images[idx] == null) return null; // Skip deleted images
                    const previewUrl = URL.createObjectURL(file);
                    return (
                        <div key={idx} style={{ display: 'flex', flexDirection: 'row', gap: '20px', width: '100%', alignItems: 'center'}}>
                            <Image
                                key={`${file.name}-${idx}`}
                                src={previewUrl}
                                alt={file.name}
                                width="150"
                                preview
                            />
                            <InputText value={images[idx].caption} onChange={(e) => setCaption(idx, e.target.value)} style={{width: "100%", height: "min-content"}}/>
                            <div style={{ display: 'flex', gap: '8px', width: '30%' }}>
                            <ButtonGroup>
                                <Button size="small" icon="pi pi-arrow-up" severity="secondary" tooltip="Move Up" disabled={idx === 0} onClick={() => moveImage(idx, -1)}/>
                                <Button size="small" icon="pi pi-arrow-down" severity="secondary" tooltip="Move Down" disabled={idx === images.length - 1} onClick={() => moveImage(idx,  1)}/>
                            </ButtonGroup>
                            <Button size="small" icon="pi pi-trash" severity="danger" onClick={() => deleteImage(idx)}/>
                            </div>
                        </div>
                    );
                })}
            </div>

            <FileUpload
                ref={fileUploadRef}
                name="images"
                accept="image/*"
                customUpload
                uploadHandler={handleNewImages}
                maxFileSize={10000000}
                mode="basic"
                auto
                chooseLabel='Upload Image'
            />
        </div>
    );
}