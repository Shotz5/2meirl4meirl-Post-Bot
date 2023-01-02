import StandardLayout from '@/Layouts/StandardLayout';
import ImageTable from '@/Layouts/ImageTable';
import { Head } from '@inertiajs/inertia-react';

export default function Images({ rows, header }) {
    return (
        <StandardLayout
            header={<h2 className="font-semibold text-xl text-gray-800 leading-tight">Images</h2>}
        >

        <Head title="Images" />

        <ImageTable header={header} rows={rows} />

        </StandardLayout>
    );
}