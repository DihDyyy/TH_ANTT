import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home() {
  return (
    <Layout title="Bài thực hành 6" description="Bảo mật với DevSecOps">
      <main>
        <header className="hero hero--primary lab-hero">
          <div className="container">
            <p className="lab-eyebrow">THỰC HÀNH LẬP TRÌNH AN NINH THÔNG TIN</p>
            <h1 className="hero__title">Bảo mật với DevSecOps</h1>
            <p className="hero__subtitle">Bài 6 · GitLab CI/CD · Docusaurus · GitLab Pages</p>
            <Link className="button button--secondary button--lg" to="/docs/lab06">
              Xem nội dung thực hành
            </Link>
          </div>
        </header>
        <section className="container lab-content">
          <h2>Từ mã nguồn đến triển khai</h2>
          <div className="row">
            {[
              ['Build', 'Cài dependencies và build website vào thư mục build/.'],
              ['Test', 'Hiểu job, stage, log và nguyên tắc dừng khi job thất bại.'],
              ['Deploy', 'Nhận artifacts và xuất bản public/ bằng GitLab Pages.'],
            ].map(([title, text]) => (
              <div className="col col--4" key={title}>
                <article className="card lab-card">
                  <div className="card__body"><h3>{title}</h3><p>{text}</p></div>
                </article>
              </div>
            ))}
          </div>
          <p className="lab-note">Trạng thái triển khai thực tế được ghi trong báo cáo và log pipeline.</p>
        </section>
      </main>
    </Layout>
  );
}
